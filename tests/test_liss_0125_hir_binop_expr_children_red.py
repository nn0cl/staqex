"""LISS-0125: HIR must not crash on BinOp during when/LINEAR walks."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_when_with_binop_does_not_raise_attribute_error() -> None:
    """Inventory red B03/A01 family: BinOp under when must not crash HIR."""
    src = """
package t
pub fn main() -> Unit {
  State a = |0>
  State b = |1>
  State r = mix (a) {
    |0> => b
    |1> => a
  }
  // Force a BinOp into an expression tree walked with when-related LINEAR
  // analysis (control arithmetic / comparison paths).
  State flag = mix (a) {
    |0> => |0>
    else => |1>
  }
  Int n = 1 + 2
  measure r
  measure flag
}
"""
    try:
        result = compile_source(src)
    except AttributeError as exc:
        raise AssertionError(
            f"compile_source raised AttributeError (LISS-0125): {exc}"
        ) from exc
    assert result is not None
    assert not any(
        "has no attribute 'left'" in str(d) for d in (result.diagnostics or [])
    )


def test_binop_in_when_scrutinee_position_does_not_crash() -> None:
    """Closer to failure_worldline / attention toys that nest BinOp near when."""
    src = """
package t
pub fn main() -> Unit {
  State q = |0>
  // Comparison BinOp as classical-ish tree near quantum control surface.
  mix (q) {
    |0> => {
      Int x = 0 + 1
    }
    else => {
      Int y = 2 * 3
    }
  }
  measure q
}
"""
    try:
        result = compile_source(src)
    except AttributeError as exc:
        raise AssertionError(
            f"compile_source raised AttributeError (LISS-0125): {exc}"
        ) from exc
    assert result is not None


def test_basics_b03_entry_does_not_crash_compile() -> None:
    from pathlib import Path

    path = Path("examples/basics/B03_failure_worldline/failure_worldline.sqx")
    src = path.read_text(encoding="utf-8")
    try:
        result = compile_source(src)
    except AttributeError as exc:
        raise AssertionError(
            f"B03 compile raised AttributeError (LISS-0125): {exc}"
        ) from exc
    assert result is not None


if __name__ == "__main__":
    test_when_with_binop_does_not_raise_attribute_error()
    test_binop_in_when_scrutinee_position_does_not_crash()
    test_basics_b03_entry_does_not_crash_compile()
    print("PASS: LISS-0125 Red/Green suite")
