"""AT-TDD Phase 1 Red: LISS-0038 semantic discrete carriers.

These tests state the reviewed boundary before the carrier types are added to
the Kernel. They are expected to fail until the type surface and phase checks
are implemented.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_semantic_carrier_declarations_are_accepted() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Dimension sites = 8
            Index<8> i = index(0)
            Basis<8> basis = basis(0)
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_index_and_basis_are_not_implicitly_interchangeable() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Basis<8> basis = basis(0)
            Index<8> i = basis
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert "SEMANTIC_CARRIER_MISMATCH_ERROR" in codes


def test_execution_counts_cannot_enter_theory_values() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            ShotCount shots = 1000
            Index<8> i = shots
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert "PHASE_TYPE_VISIBILITY_ERROR" in codes


def test_same_machine_representation_does_not_enable_arithmetic() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Index<8> i = index(0)
            ShotCount shots = 1000
            State invalid = i + shots
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert "SEMANTIC_CARRIER_OPERATION_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_semantic_carrier_declarations_are_accepted,
        test_index_and_basis_are_not_implicitly_interchangeable,
        test_execution_counts_cannot_enter_theory_values,
        test_same_machine_representation_does_not_enable_arithmetic,
    ):
        test()
    print("OK — semantic discrete carrier tests")
