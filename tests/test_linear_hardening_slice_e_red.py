"""AT-TDD Phase 1 Red: LISS-0114 Slice E — when / nested-block lifetime."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def _linear(diags: list[dict]) -> set[str]:
    return {
        c
        for c in _codes(diags)
        if c.startswith("LINEAR_") or c == "UNCOMPUTE_WITNESS_MISSING"
    }


def test_foreach_inner_discard_is_detected() -> None:
    """R6: leftover State inside ForEach body must LINEAR_IMPLICIT_DISCARD."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> wires = QubitRegister(1)
            ForEach w in wires {
                State<Int> leftover = Coin()
            }
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(compiled.diagnostics), (
        f"expected nested discard, got {compiled.diagnostics}"
    )
    assert compiled.ok is False


def test_when_scrutinee_counts_as_consume() -> None:
    """R6: Mix (bit) consumes bit so it is not an implicit discard."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> bit = Coin()
            State<Int> label = Mix (bit) {
              0 -> 0,
              else -> 1,
            }
            Measure label
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(compiled.diagnostics), (
        f"when scrutinee must consume bit, got {compiled.diagnostics}"
    )
    assert not _linear(compiled.diagnostics), compiled.diagnostics
    assert compiled.ok, compiled.diagnostics


def test_when_arm_var_use_consumes_outer_root() -> None:
    """Vars referenced in when arms consume those linear roots."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> bit = Coin()
            State<Int> a = Coin()
            State<Int> b = Coin()
            State<Int> q = Mix (bit) {
              0 -> a,
              else -> b,
            }
            Measure q
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(compiled.diagnostics), (
        f"arm uses of a/b and Mix (bit) must consume, got {compiled.diagnostics}"
    )
    assert not _linear(compiled.diagnostics), compiled.diagnostics
    assert compiled.ok, compiled.diagnostics


def main() -> None:
    test_foreach_inner_discard_is_detected()
    print("PASS test_foreach_inner_discard_is_detected")
    test_when_scrutinee_counts_as_consume()
    print("PASS test_when_scrutinee_counts_as_consume")
    test_when_arm_var_use_consumes_outer_root()
    print("PASS test_when_arm_var_use_consumes_outer_root")
    print("OK - LISS-0114 Slice E Phase 1 Red")


if __name__ == "__main__":
    main()
