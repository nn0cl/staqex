"""AT-TDD LISS-0228: Joint apply(qft/iqft/cqft) runtime."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def test_qft_iqft_roundtrip_two_wires() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  QubitRegister<2> reg = system()
  Operator F = qft(reg)
  Operator Fi = iqft(reg)
  State a = |0>
  State b = |1>
  State (a, b) = apply(F, a, b)
  State (a, b) = apply(Fi, a, b)
  State a = |0>
  Measure b
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics
    msgs = " ".join(str(d.get("message", "")) for d in result.diagnostics)
    assert "cannot compile operator node Call" not in msgs


def test_cqft_apply_three_wires() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  QubitRegister<1> ctrl = system()
  QubitRegister<2> reg = system()
  Operator CF = cqft(ctrl, reg)
  State c = |1>
  State t0 = |0>
  State t1 = |0>
  State (c, t0, t1) = apply(CF, c, t0, t1)
  State t0 = |0>
  State t1 = |0>
  Measure c
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


if __name__ == "__main__":
    test_qft_iqft_roundtrip_two_wires()
    test_cqft_apply_three_wires()
    print("PASS LISS-0228")
