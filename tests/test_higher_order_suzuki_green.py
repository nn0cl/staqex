"""Phase 2 Green checks for ADR 0084 S2 lowering and provenance."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.codegen_qasm import OpenQASM3Generator  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _source(policy: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        Operator H = X + Z
        State psi = |0>
        State evolved = evolve {{ psi under H for 1.0.s using Suzuki(order = 2, {policy}) }}.run()
        State psi = |0>
        measure evolved
    }}
    """


def test_suzuki_direct_steps_lower_to_qasm_and_null_provenance() -> None:
    compiled = compile_source(_source("steps = 2"))
    assert compiled.ok, compiled.diagnostics
    policy = compiled.qpu_ir["lowering_policy"]
    assert policy == {
        "algorithm": "Suzuki",
        "order": 2,
        "steps": 2,
        "error_mode": None,
        "tolerance_target": None,
    }
    emitted = OpenQASM3Generator(route=False).generate_detailed(compiled.unit)
    assert emitted.ok, emitted.notes
    assert any("suzuki S2 step 1/2" in (gate.comment or "") for gate in emitted.circuit.gates)


def test_suzuki_tolerance_derives_static_steps_for_each_error_mode() -> None:
    bound = compile_source(_source("tolerance = 1e-4, error = Bound"))
    empirical = compile_source(
        _source("tolerance = 1e-4, error = EmpiricalEstimate")
    )
    assert bound.ok and empirical.ok
    bound_policy = bound.qpu_ir["lowering_policy"]
    empirical_policy = empirical.qpu_ir["lowering_policy"]
    assert bound_policy["error_mode"] == "Bound"
    assert empirical_policy["error_mode"] == "EmpiricalEstimate"
    assert bound_policy["steps"] > empirical_policy["steps"] >= 1

