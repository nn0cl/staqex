"""Phase 1 acceptance tests for LISS-0437.

These tests specify only the reviewed source/compiler contract; they do not
assert an internal IR, numerical equivalence, QPU resource estimate, or
perform corpus migration.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.host import run_source as host_run_source  # noqa: E402
from compiler.staqex.backend.qasm.lower import (  # noqa: E402
    EvolutionTargetProfile,
    lower_unit_to_circuit,
)


def _codes(source: str) -> set[str]:
    return {str(d.get("code", "")) for d in compile_source(source).diagnostics}


def test_explicit_propagator_and_state_application_are_accepted() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dur = 0.6.fs
            State psi = |0>
            Operator U_t = exp(-i * H * dur / hbar)
            State evolved = Evolve() { U_t * psi }.run()
            Measure evolved
        }
        """
    )
    assert not codes, codes


def test_bare_state_is_not_promoted_to_evolution() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            State evolved = Evolve() { psi }.run()
            Measure evolved
        }
        """
    )
    assert "EVOLVE_REQUIRES_EXPLICIT_TRANSFORM" in codes


def test_explicit_propagator_executes_in_the_kernel() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dur = 0.1.fs
            State psi = |0>
            State prepared = apply(X, psi)
            Operator U_t = exp(-i * H * dur / hbar)
            State evolved = Evolve() { U_t * prepared }.run()
            Measure evolved
        }
    """
    run_source(source)


def test_explicit_propagator_preserves_tuple_carriers_for_terminal_trace_out() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * (Z[0] * Z[1])
            Time dur = 0.1.fs
            s0, s1 = |+>, |+>
            Operator U_t = exp(-i * H * dur / hbar)
            State (s0, s1) = Evolve() { U_t * (s0, s1) }.run()
            State zz = expect(ZZ, s0, s1)
            Measure s0 tracing_out s1
        }
    """
    result = compile_source(source)
    assert result.ok, result.diagnostics
    run_source(source)


def test_explicit_propagator_accepts_dimensioned_operator_from_function() -> None:
    source = """
        package t
        struct Couplings { J: Energy }
        fn ising_hamiltonian(c: Couplings) -> Operator {
            return -c.J * (Z[0] * Z[1])
        }
        pub fn main() -> Unit {
            Couplings c = Couplings { J: 1.0.eV to J }
            Operator H = ising_hamiltonian(c)
            Time dur = 0.1.fs
            Operator U_t = exp(-i * H * dur / hbar)
            State psi = |0>
            State evolved = Evolve() { U_t * psi }.run()
            Measure evolved
        }
    """
    result = compile_source(source)
    assert result.ok, result.diagnostics


def test_explicit_propagator_preserves_dimension_through_identity_operator_sum() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            Energy offset = 0.7.eV to J
            Operator electronic = X
            Operator H = electronic + offset * I
            Time dur = 0.1.fs
            Operator U_t = exp(-i * H * dur / hbar)
            State psi = |0>
            State evolved = Evolve() { U_t * psi }.run()
            Measure evolved
        }
    """
    result = compile_source(source)
    assert result.ok, result.diagnostics


def test_explicit_propagator_preserves_dimension_through_operator_local_return() -> None:
    source = """
        package t
        fn build_hamiltonian() -> Operator {
            Energy scale = 0.7.eV to J
            Operator H = scale * X
            return H
        }
        pub fn main() -> Unit {
            Operator H = build_hamiltonian()
            Time dur = 0.1.fs
            Operator U_t = exp(-i * H * dur / hbar)
            State psi = |0>
            State evolved = Evolve() { U_t * psi }.run()
            Measure evolved
        }
    """
    result = compile_source(source)
    assert result.ok, result.diagnostics


def test_qpu_lowering_rejects_explicit_evolution_without_partial_circuit() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dur = 0.1.fs
            State psi = |0>
            State prepared = apply(X, psi)
            Operator U_t = exp(-i * H * dur / hbar)
            State evolved = Evolve() { U_t * prepared }.run()
            Measure evolved
        }
    """
    circuit = lower_unit_to_circuit(compile_source(source).unit)
    assert circuit.reject_code == "EVOLUTION_TARGET_UNSUPPORTED"
    assert not circuit.gates


def test_qpu_target_profile_realizes_explicit_exponential_with_suzuki() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dur = 0.1.fs
            State psi = |0>
            Operator U_t = exp(-i * H * dur / hbar)
            State evolved = Evolve() { U_t * psi }.run()
            Measure evolved
        }
    """
    result = compile_source(source)
    circuit = lower_unit_to_circuit(
        result.unit,
        target_profile=EvolutionTargetProfile(suzuki_order=2, suzuki_steps=2),
    )
    assert circuit.reject_code is None
    assert any("suzuki" in gate.comment for gate in circuit.gates)
    assert any("resource_estimate" in note for note in circuit.notes)


def test_qpu_target_profile_rejects_invalid_suzuki_policy() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dur = 0.1.fs
            State psi = |0>
            State prepared = apply(X, psi)
            Operator U_t = exp(-i * H * dur / hbar)
            State evolved = Evolve() { U_t * prepared }.run()
            Measure evolved
        }
    """
    result = compile_source(source)
    circuit = lower_unit_to_circuit(
        result.unit,
        target_profile=EvolutionTargetProfile(suzuki_order=3, suzuki_steps=0),
    )
    assert circuit.reject_code in {"SUZUKI_ORDER_ERROR", "SUZUKI_POLICY_ERROR"}
    assert not circuit.gates


def test_qpu_profile_rejects_written_positive_i_without_rewriting_physics() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dur = 0.1.fs
            State psi = |0>
            Operator U_t = exp(i * H * dur / hbar)
            State evolved = Evolve() { U_t * psi }.run()
            Measure evolved
        }
    """
    result = compile_source(source)
    circuit = lower_unit_to_circuit(
        result.unit,
        target_profile=EvolutionTargetProfile(suzuki_order=2, suzuki_steps=2),
    )
    assert circuit.reject_code == "EVOLUTION_TARGET_UNSUPPORTED"
    assert not circuit.gates


def _bounded_source(*, predicate: str = "converged(fuel)", max_steps: str = "4") -> str:
    return f"""
        package t
        pub fn main() -> Unit {{
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dt = 0.1.fs
            State fuel = |0>
            Operator U_dt = exp(-i * H * dt / hbar)
            State result = Evolve() {{
                U_dt * fuel
                until {predicate}
                max {max_steps}
            }}.run()
            Measure result
        }}
    """


def test_bounded_explicit_evolution_is_accepted_in_blackboard_order() -> None:
    result = compile_source(_bounded_source())
    assert result.ok, result.diagnostics


def test_bounded_explicit_evolution_rejects_non_positive_or_dynamic_max() -> None:
    zero = compile_source(_bounded_source(max_steps="0"))
    dynamic = compile_source(
        _bounded_source(max_steps="limit")
        .replace("State fuel = |0>", "Int limit = 4\n            State fuel = |0>")
    )
    assert "EVOLVE_UNTIL_BOUND_ERROR" in {
        str(d.get("code", "")) for d in zero.diagnostics
    }
    assert "EVOLVE_UNTIL_BOUND_ERROR" in {
        str(d.get("code", "")) for d in dynamic.diagnostics
    }


def test_bounded_explicit_evolution_runs_stepwise_and_checks_after_a_step() -> None:
    result = host_run_source(
        _bounded_source().replace("1.0.eV", "0.0.eV"),
        settings={"target": "local", "seed": 7},
    )
    assert result.status == "succeeded", result.diagnostics
    provenance = result.metadata["evolution_provenance"]
    assert provenance["iteration_count"] >= 1
    assert provenance["metric"] == "full_state_l2_difference"
    assert provenance["numeric_type"] == "Float64"
    assert provenance["tolerance"] == 1e-9


def test_bounded_explicit_evolution_exhaustion_is_atomic_and_reports_provenance() -> None:
    result = host_run_source(
        _bounded_source(predicate="false", max_steps="2"),
        settings={"target": "local", "seed": 7},
    )
    assert result.status == "failed"
    assert any(
        d.get("code") == "EVOLVE_UNTIL_MAX_STEPS_ERROR"
        for d in result.diagnostics
    )
    provenance = result.metadata["evolution_provenance"]
    assert provenance["stop_reason"] == "max_exhausted"
    assert provenance["iteration_count"] == provenance["max_steps"] == 2
    assert "state" not in result.metadata
    assert not result.measurements


def test_bounded_predicate_is_non_collapsing_for_tuple_state() -> None:
    source = _bounded_source().replace("1.0.eV", "0.0.eV").replace(
        "State fuel = |0>",
        "s0, s1 = |+>, |+>",
    ).replace("State result = Evolve()", "State (s0, s1) = Evolve()").replace(
        "Measure result", "Measure s0 tracing_out s1"
    ).replace("U_dt * fuel", "U_dt * (s0, s1)").replace(
        "converged(fuel)", "converged(s0)"
    )
    result = host_run_source(source, settings={"target": "local", "seed": 7})
    assert result.status == "succeeded", result.diagnostics
    assert result.metadata["evolution_provenance"]["predicate_effect"] == "non_collapsing"


def test_qpu_rejects_bounded_dynamic_termination_before_allocation() -> None:
    result = compile_source(_bounded_source())
    circuit = lower_unit_to_circuit(result.unit)
    assert circuit.reject_code == "E_QPU_UNSUPPORTED_CAPABILITY"
    assert not circuit.gates


def test_times_and_for_remain_separate_from_bounded_explicit_mode() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            State a = |0>
            State a = Evolve (a) times 2 { a }
            State a = Evolve (a) for 0.1.fs { a }
            Measure a
        }
    """
    result = compile_source(source)
    assert result.ok, result.diagnostics

    legacy_until = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            Operator H = X
            State evolved = Evolve { psi under H for 0.6.s until converged(psi) max 2 }.run()
            Measure evolved
        }
        """
    )
    assert "EVOLVE_UNTIL_MODE_ERROR" in {
        d.get("code") for d in legacy_until.diagnostics
    }


def test_legacy_hamiltonian_shortcut_fails_closed_with_migration_diagnostic() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            State evolved = Evolve { psi under H for 0.6.s }.run()
            Measure evolved
        }
        """
    )
    assert "EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED" in codes


def test_strict_migration_profile_rejects_legacy_hamiltonian_shortcut() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            Operator H = X
            State evolved = Evolve { psi under H for 0.6.s }.run()
            Measure evolved
        }
    """
    assert "EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED" in {
        d.get("code") for d in compile_source(source).diagnostics
    }
    assert not compile_source(source, strict_evolution=True).ok


def test_operator_exponent_requires_dimensionless_exponent() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            State psi = |0>
            Operator bad = exp(H)
            State evolved = Evolve() { bad * psi }.run()
            Measure evolved
        }
        """
    )
    assert "EVOLUTION_DIMENSION_ERROR" in codes


def test_limit_is_source_preserving_but_requires_target_realization() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            State psi = |0>
            Operator U_t = Limit N -> Infinity {
                (I - i * H * 0.6.s / (N * hbar)) ^ N
            }
            State evolved = Evolve() { U_t * psi }.run()
            Measure evolved
        }
        """
    )
    assert "EVOLUTION_REALIZATION_REQUIRED" in codes


def test_s02_fixture_exposes_propagator_application_without_claiming_equivalence() -> None:
    source = (_REPO / "examples/showcase/S02_drug_discovery/main_selection.sqx").read_text()
    assert "Operator U_t = exp(-i * H_obj * dur / hbar)" in source
    assert "Evolve()" in source
    assert "U_t * psi_sel" in source
    assert "Measure psi_final" in source


if __name__ == "__main__":
    test_explicit_propagator_and_state_application_are_accepted()
    test_bare_state_is_not_promoted_to_evolution()
    test_explicit_propagator_executes_in_the_kernel()
    test_explicit_propagator_preserves_tuple_carriers_for_terminal_trace_out()
    test_explicit_propagator_accepts_dimensioned_operator_from_function()
    test_explicit_propagator_preserves_dimension_through_identity_operator_sum()
    test_explicit_propagator_preserves_dimension_through_operator_local_return()
    test_qpu_lowering_rejects_explicit_evolution_without_partial_circuit()
    test_qpu_target_profile_realizes_explicit_exponential_with_suzuki()
    test_qpu_target_profile_rejects_invalid_suzuki_policy()
    test_qpu_profile_rejects_written_positive_i_without_rewriting_physics()
    test_strict_migration_profile_rejects_legacy_hamiltonian_shortcut()
    test_legacy_hamiltonian_shortcut_fails_closed_with_migration_diagnostic()
    test_operator_exponent_requires_dimensionless_exponent()
    test_limit_is_source_preserving_but_requires_target_realization()
    test_s02_fixture_exposes_propagator_application_without_claiming_equivalence()
    test_bounded_explicit_evolution_is_accepted_in_blackboard_order()
    test_bounded_explicit_evolution_rejects_non_positive_or_dynamic_max()
    test_bounded_explicit_evolution_runs_stepwise_and_checks_after_a_step()
    test_bounded_explicit_evolution_exhaustion_is_atomic_and_reports_provenance()
    test_bounded_predicate_is_non_collapsing_for_tuple_state()
    test_qpu_rejects_bounded_dynamic_termination_before_allocation()
    test_times_and_for_remain_separate_from_bounded_explicit_mode()
    print("GREEN — LISS-0437 explicit evolution surface")
