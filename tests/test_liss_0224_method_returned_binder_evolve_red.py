"""AT-TDD LISS-0224: method-returned finite binders must evolve."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _method_returned_binder_source() -> str:
    return """
package t
namespace G {
  pub class L {
    fn init() {}
    pub fn h() -> Operator {
      Operator H = sum (i in Index<0..2>) { 1.0545718e-19 * Z[i] }
      return H
    }
  }
}
pub fn main() -> Unit {
  G.L lat = G.L()
  Operator H = lat.h()
  State a = |+>
  State b = |0>
  State c = |0>
  State (a, b, c) = evolve { (a, b, c) under H for 0.1.fs using Suzuki(order = 2, steps = 2) }.run()
  State b = |0>
  State c = |0>
  measure a
}
"""


def _top_level_binder_source() -> str:
    return """
package t
pub fn main() -> Unit {
  Operator H = sum (i in Index<0..2>) { 1.0545718e-19 * Z[i] }
  State a = |+>
  State b = |0>
  State c = |0>
  State (a, b, c) = evolve { (a, b, c) under H for 0.1.fs using Suzuki(order = 2, steps = 2) }.run()
  State b = |0>
  State c = |0>
  measure a
}
"""


def test_method_returned_sum_binder_evolves() -> None:
    result = run_source(
        _method_returned_binder_source(),
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics
    codes = {d.get("code") for d in result.diagnostics}
    assert "RUNTIME_ERROR" not in codes


def test_top_level_sum_binder_still_evolves() -> None:
    result = run_source(
        _top_level_binder_source(),
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


if __name__ == "__main__":
    test_method_returned_sum_binder_evolves()
    test_top_level_sum_binder_still_evolves()
    print("PASS LISS-0224")
