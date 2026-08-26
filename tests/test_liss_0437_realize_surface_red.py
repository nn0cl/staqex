"""Phase 1 Red acceptance tests for explicit Realize(source=...) syntax."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import Call, StateBind, Var  # noqa: E402
from compiler.staqex.backend.qasm.lower import EvolutionTargetProfile, lower_unit_to_circuit  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


_SOURCE = """
package t
pub fn main() -> Unit {
    Operator U_formal = Limit N -> Infinity {
        (I - i * H * dur / (N * hbar)) ^ N
    }
    Operator U_qpu = Realize(
        source = U_formal,
        method = "suzuki",
        order = 2,
        steps = 8,
        error_budget = 1e-6
    )
    Measure |0>
}
"""


def test_realize_is_a_visible_typed_conversion_boundary() -> None:
    compiled = compile_source(_SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    binding = next(
        statement
        for statement in compiled.unit.main.body.stmts
        if isinstance(statement, StateBind) and statement.names == ["U_qpu"]
    )
    assert isinstance(binding.expr, Call)
    assert isinstance(binding.expr.callee, Var)
    assert binding.expr.callee.name == "Realize"
    kwargs = dict(binding.expr.kwargs or ())
    assert isinstance(kwargs["source"], Var)
    assert kwargs["source"].name == "U_formal"
    assert kwargs["method"].value == "suzuki"
    assert kwargs["order"].value == 2
    assert kwargs["steps"].value == 8
    assert kwargs["error_budget"].value == 1e-6


def test_realize_preserves_formal_and_realized_operator_provenance() -> None:
    compiled = compile_source(_SOURCE)
    assert compiled.evolution_provenance
    assert compiled.evolution_provenance["source_name"] == "U_formal"
    assert compiled.evolution_provenance["realized_name"] == "U_qpu"
    assert compiled.evolution_provenance["source_transform"] == (
        "Limit product of infinitesimal steps"
    )
    assert compiled.evolution_provenance["method"] == "suzuki"
    assert compiled.evolution_provenance["order"] == 2
    assert compiled.evolution_provenance["steps"] == 8
    assert compiled.evolution_provenance["error_budget"] == 1e-6
    assert compiled.evolution_provenance["state_shape"] == "Operator"
    assert compiled.evolution_provenance["approximation_order_or_null"] == 2
    assert compiled.evolution_provenance["approximation_steps_or_null"] == 8
    assert compiled.evolution_provenance["error_budget_or_null"] == 1e-6
    assert compiled.evolution_provenance["capability_rejection_or_null"] is None


def test_direct_limit_never_infers_realize_or_fixed_n() -> None:
    direct_source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H = scale * X
        Time dur = 0.6.fs
        Operator U_t = Limit N -> Infinity {
            (I - i * H * dur / (N * hbar)) ^ N
        }
        State psi = |0>
        State result = Evolve() { U_t * psi }.run()
        Measure result
    }
    """
    compiled = compile_source(direct_source)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            limit_realization_method="suzuki",
            limit_order=2,
            limit_steps=8,
            limit_error_budget=1e-6,
        ),
    )
    assert circuit.reject_code == "EVOLUTION_REALIZATION_REQUIRED"
    assert circuit.provenance
    assert circuit.provenance["capability_rejection_or_null"] == (
        "EVOLUTION_REALIZATION_REQUIRED"
    )
    assert not circuit.gates


def test_unrelated_direct_limit_remains_rejected_when_realize_is_present() -> None:
    mixed_source = _SOURCE.replace(
        "    Operator U_qpu = Realize(\n",
        "    Operator U_direct = Limit N -> Infinity {\n"
        "        (I - i * H * dur / (N * hbar)) ^ N\n"
        "    }\n"
        "    Operator U_qpu = Realize(\n",
    )
    compiled = compile_source(mixed_source)
    assert any(
        diagnostic.get("code") == "EVOLUTION_REALIZATION_REQUIRED"
        for diagnostic in compiled.diagnostics
    )


def test_realize_rejects_unknown_named_arguments() -> None:
    source = _SOURCE.replace(
        '        error_budget = 1e-6\n',
        '        error_budget = 1e-6,\n'
        '        hidden_n = 8\n',
    )
    compiled = compile_source(source)
    assert any(
        diagnostic.get("code") == "EVOLUTION_REALIZATION_POLICY_ERROR"
        and "hidden_n" in diagnostic.get("message", "")
        for diagnostic in compiled.diagnostics
    )


if __name__ == "__main__":
    tests = [
        test_realize_is_a_visible_typed_conversion_boundary,
        test_realize_preserves_formal_and_realized_operator_provenance,
        test_direct_limit_never_infers_realize_or_fixed_n,
        test_unrelated_direct_limit_remains_rejected_when_realize_is_present,
        test_realize_rejects_unknown_named_arguments,
    ]
    failures: list[str] = []
    for test in tests:
        try:
            test()
        except AssertionError as error:
            failures.append(f"{test.__name__}: AssertionError: {error}")
        except Exception as error:  # noqa: BLE001 - Red runner collects all cases.
            failures.append(f"{test.__name__}: {type(error).__name__}: {error}")
    for failure in failures:
        print(f"RED: {failure}")
    if not failures:
        print(f"GREEN: {len(tests)}/{len(tests)} Realize boundary checks passed")
    else:
        print(f"RED: {len(failures)}/{len(tests)} failing")
