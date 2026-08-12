"""AT-TDD Phase 1 Red: LISS-0114 Slice F — runtime uncompute + tolerance."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def test_uncompute_tolerance_exported() -> None:
    from compiler.staqex import hir as hir_mod
    from compiler.staqex.runtime.numeric_policy import PHYSICAL_TOLERANCE
    from compiler.staqex.runtime import uncompute as uc

    assert hasattr(hir_mod, "LINEAR_UNCOMPUTE_AMPLITUDE_TOL")
    assert hir_mod.LINEAR_UNCOMPUTE_AMPLITUDE_TOL == PHYSICAL_TOLERANCE
    assert uc.LINEAR_UNCOMPUTE_AMPLITUDE_TOL == PHYSICAL_TOLERANCE
    assert abs(uc.LINEAR_UNCOMPUTE_AMPLITUDE_TOL - 1e-12) < 1e-18


def test_is_computational_basis_zero_accepts_ket0() -> None:
    from compiler.staqex.runtime.joint import Joint, World
    from compiler.staqex.runtime.uncompute import is_computational_basis_zero

    joint = Joint(worlds=[World(assign={"q": 0}, amp=1.0 + 0.0j)])
    assert is_computational_basis_zero(joint, "q")


def test_is_computational_basis_zero_rejects_one() -> None:
    from compiler.staqex.runtime.joint import Joint, World
    from compiler.staqex.runtime.uncompute import (
        is_computational_basis_zero,
        require_computational_basis_zero,
    )

    joint = Joint(worlds=[World(assign={"q": 1}, amp=1.0 + 0.0j)])
    assert not is_computational_basis_zero(joint, "q")
    try:
        require_computational_basis_zero(joint, "q")
    except ValueError as exc:
        assert "UNCOMPUTE_RUNTIME_MISMATCH" in str(exc)
    else:
        raise AssertionError("expected UNCOMPUTE_RUNTIME_MISMATCH")


def test_static_uncompute_program_runs_under_runtime_check() -> None:
    """effects { Uncompute } + |0> witness must run without runtime mismatch."""
    from compiler.staqex.host import run_source

    result = run_source(
        """
        package t
        fn reset_ancilla() -> State<Int> effects { Uncompute } {
            State<Int> ancilla = Coin()
            State<Int> ancilla = |0>
            return ancilla
        }
        pub fn main() -> Unit {
            State<Int> a = reset_ancilla()
            Measure a
        }
        """
    )
    assert result.status == "succeeded", (
        f"expected succeeded, got {result.status}: {result.diagnostics}"
    )


def test_adr_candidate_documents_tolerance() -> None:
    adr = (
        _REPO
        / "docs/architecture/decision-themes/dec-0002-state-first-semantics-and-measurement.md"
    )
    assert adr.is_file(), "expected Proposed ADR 0107 for uncompute tolerance"
    text = adr.read_text(encoding="utf-8")
    assert "1e-12" in text
    assert "Accepted" in text


def main() -> None:
    test_uncompute_tolerance_exported()
    print("PASS test_uncompute_tolerance_exported")
    test_is_computational_basis_zero_accepts_ket0()
    print("PASS test_is_computational_basis_zero_accepts_ket0")
    test_is_computational_basis_zero_rejects_one()
    print("PASS test_is_computational_basis_zero_rejects_one")
    test_static_uncompute_program_runs_under_runtime_check()
    print("PASS test_static_uncompute_program_runs_under_runtime_check")
    test_adr_candidate_documents_tolerance()
    print("PASS test_adr_candidate_documents_tolerance")
    print("OK - LISS-0114 Slice F Phase 1 Red")


if __name__ == "__main__":
    main()
