"""AT-TDD Phase 1 Red: LISS-0114 Slice B — consume-set policy + R3 Measure-reuse."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def test_linear_consume_kinds_documented() -> None:
    """R1: Hir module must export the authoritative linear consume-kind set."""
    from compiler.staqex import hir as hir_mod

    assert hasattr(hir_mod, "LINEAR_CONSUME_KINDS"), (
        "expected LINEAR_CONSUME_KINDS documenting Measure ∪ static uncompute"
    )
    kinds = hir_mod.LINEAR_CONSUME_KINDS
    assert "Measure" in kinds
    assert "static_uncompute_zero_reset" in kinds
    # Gate / apply / hadamard rebinds are explicitly non-consume.
    assert "gate_apply" not in kinds
    assert "hadamard" not in kinds


def test_second_measure_emits_linear_duplicate_use() -> None:
    """R3: measuring an already-consumed root emits LINEAR_DUPLICATE_USE.

    Early-collapse may also fire (non-terminal Measure); linear must still name
    the reuse.
    """
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            Measure q
            Measure q
        }
        """
    )
    assert "LINEAR_DUPLICATE_USE" in _codes(compiled.diagnostics), (
        f"expected LINEAR_DUPLICATE_USE on second Measure, got "
        f"{compiled.diagnostics}"
    )
    assert compiled.ok is False


def test_gate_rebind_does_not_consume() -> None:
    """R1: hadamard/apply-style rebind is not a linear consume."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            State<Int> q = hadamard(q)
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(compiled.diagnostics), (
        f"gate rebind must not count as consume; expected discard, got "
        f"{compiled.diagnostics}"
    )
    assert "LINEAR_DUPLICATE_USE" not in _codes(compiled.diagnostics)


def test_gate_rebind_then_single_measure_is_accepted() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            State<Int> q = hadamard(q)
            Measure q
        }
        """
    )
    assert "LINEAR_DUPLICATE_USE" not in _codes(compiled.diagnostics)
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(compiled.diagnostics)
    assert compiled.ok, compiled.diagnostics


def main() -> None:
    test_linear_consume_kinds_documented()
    print("PASS test_linear_consume_kinds_documented")
    test_second_measure_emits_linear_duplicate_use()
    print("PASS test_second_measure_emits_linear_duplicate_use")
    test_gate_rebind_does_not_consume()
    print("PASS test_gate_rebind_does_not_consume")
    test_gate_rebind_then_single_measure_is_accepted()
    print("PASS test_gate_rebind_then_single_measure_is_accepted")
    print("OK - LISS-0114 Slice B Phase 1 Red")


if __name__ == "__main__":
    main()
