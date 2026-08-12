"""AT-TDD Phase 1 Red: LISS-0012 bounded pure Evolve-until."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_bounded_evolve_until_is_a_state_preserving_expression() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = Dirac(0)
            State result = Evolve { psi under X for 1 until converged(psi) max 64 }.run()
            State psi = |0>
            Measure result
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_qpu_emission_rejects_evolve_until_at_the_backend_boundary() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            Operator H = Z[0]
            State psi = Dirac(0)
            State result = Evolve { psi under H for 1 using Suzuki(order = 2, steps = 1) until converged(psi) max 64 }.run()
            State psi = |0>
            Measure result
        }
        """
    )

    assert compiled.unit is not None
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert not emitted.ok
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_UNSUPPORTED_CAPABILITY"


def test_evolve_until_requires_an_explicit_positive_max() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = Dirac(0)
            State result = Evolve { psi under X for 1 until converged(psi) }.run()
            Measure result
        }
        """
    )

    assert "EVOLVE_UNTIL_BOUND_ERROR" in codes


def test_evolve_until_rejects_non_positive_max() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = Dirac(0)
            State result = Evolve { psi under X for 1 until converged(psi) max 0 }.run()
            Measure result
        }
        """
    )

    assert "EVOLVE_UNTIL_BOUND_ERROR" in codes


def test_evolve_until_predicate_cannot_measure_or_consume_rng() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = Dirac(0)
            State result = Evolve { psi under X for 1 until Measure psi max 64 }.run()
            Measure result
        }
        """
    )

    assert "EVOLVE_UNTIL_EFFECT_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_bounded_evolve_until_is_a_state_preserving_expression,
        test_qpu_emission_rejects_evolve_until_at_the_backend_boundary,
        test_evolve_until_requires_an_explicit_positive_max,
        test_evolve_until_rejects_non_positive_max,
        test_evolve_until_predicate_cannot_measure_or_consume_rng,
    ):
        test()
    print("OK — Evolve until Red tests")
