"""AT-TDD Phase 1 Red: LISS-0031 operator algebra."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_adjoint_and_commutator_are_typed_operator_forms() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator A = adjoint(X)
            Operator C = commutator(A, X)
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_inner_and_outer_preserve_state_operator_boundary() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            State phi = |1>
            State overlap = inner(phi, psi)
            Operator projector = outer(psi, phi)
            State psi = |0>
            State phi = |0>
            measure overlap
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_commutator_rejects_state_operator_mismatch() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            Operator invalid = commutator(X, psi)
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert "OPERATOR_ALGEBRA_TYPE_ERROR" in codes


def test_operator_algebra_does_not_measure() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Operator invalid = adjoint(measure(|0>))
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert "EARLY_COLLAPSE_ERROR" in codes


def test_explicit_operator_domain_is_preserved() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator<Qubit> A = adjoint(X)
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_commutator_rejects_known_domain_mismatch() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Operator<Position> P = adjoint(X)
            Operator<Qubit> invalid = commutator(P, X)
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert "OPERATOR_DOMAIN_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_adjoint_and_commutator_are_typed_operator_forms,
        test_inner_and_outer_preserve_state_operator_boundary,
        test_commutator_rejects_state_operator_mismatch,
        test_operator_algebra_does_not_measure,
        test_explicit_operator_domain_is_preserved,
        test_commutator_rejects_known_domain_mismatch,
    ):
        test()
    print("OK — operator algebra tests")
