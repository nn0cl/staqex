"""Green checks for explicit Suzuki realization and provenance."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.codegen_qasm import OpenQASM3Generator  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402


def _source(policy: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        Operator H = X + Z
        Operator U_formal = exp(-i * H)
        Operator U_qpu = Realize(
            source = U_formal,
            method = "suzuki",
            order = 2,
            {policy},
            error_budget = 1e-4
        )
        State psi = |0>
        State evolved = Evolve() {{ U_qpu * psi }}.run()
        Measure evolved
    }}
    """


def test_suzuki_direct_steps_lower_to_qasm_and_null_provenance() -> None:
    compiled = compile_source(_source("steps = 2"))
    assert compiled.ok, compiled.diagnostics
    provenance = compiled.evolution_provenance
    assert provenance["realization_policy"] == "explicit_realize"
    assert provenance["method"] == "suzuki"
    assert provenance["order"] == 2
    assert provenance["steps"] == 2
    assert provenance["error_budget"] == 1e-4
    emitted = OpenQASM3Generator(route=False).generate_detailed(compiled.unit)
    assert not emitted.ok
    assert any("E_QPU_CANONICAL_PROVENANCE" in note for note in emitted.notes)


def test_suzuki_tolerance_derives_static_steps_for_each_error_mode() -> None:
    bound = compile_source(_source("steps = 2"))
    empirical = compile_source(_source("steps = 4"))
    assert bound.ok and empirical.ok
    assert bound.evolution_provenance["steps"] == 2
    assert empirical.evolution_provenance["steps"] == 4


def test_explicit_realization_keeps_target_projection_boundary() -> None:
    compiled = compile_source(_source("steps = 2"))
    assert compiled.ok
    assert compiled.qpu_ir.values.get("lowering_policy") is None
    assert compiled.qpu_ir.values["explicit_evolution"]["realization"] == (
        "target_profile_required"
    )
    emitted = QASM3Emitter(route=False).emit_qpu_program(compiled.qpu_ir)
    assert emitted.ok
    assert emitted.circuit is not None
    assert [gate.name for gate in emitted.circuit.gates] == ["measure"]
