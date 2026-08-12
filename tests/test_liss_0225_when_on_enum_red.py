"""AT-TDD LISS-0225: when on classical enum control."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _when_enum_source(variant: str) -> str:
    return f"""
package t
namespace N {{
  pub enum S {{
    Open,
    Blocked
  }}
}}
pub fn main() -> Unit {{
  N.S s = N.S.{variant}
  State w = mix (s) {{
    Open -> |1>,
    else -> |0>,
  }}
  State peeked = expect(Z, w)
  State viewed = inspect(peeked)
  measure w
}}
"""


def test_when_on_open_enum_runs() -> None:
    result = run_source(
        _when_enum_source("Open"),
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_when_on_blocked_enum_runs() -> None:
    result = run_source(
        _when_enum_source("Blocked"),
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_when_on_coin_still_runs() -> None:
    src = """
package t
pub fn main() -> Unit {
  State bit = coin()
  State w = mix (bit) {
    0 -> |0>,
    else -> |+>,
  }
  measure w
}
"""
    result = run_source(src, settings={"seed": 0}, stdout=io.StringIO())
    assert result.status == "succeeded", result.diagnostics


if __name__ == "__main__":
    test_when_on_open_enum_runs()
    test_when_on_blocked_enum_runs()
    test_when_on_coin_still_runs()
    print("PASS LISS-0225")
