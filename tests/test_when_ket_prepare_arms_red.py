"""AT-TDD: LISS-0138 when arms with ket / prepare literals."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import run_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def _run(src: str):
    return run_source(
        src,
        settings={"target": "local", "seed": 0},
        stdout=io.StringIO(),
    )


_PREPARE_PLUS = """
package t
pub fn main() -> Unit {
    State bit = Coin()
    State prep = Mix (bit) {
      0 -> |0>,
      else -> |+>,
    }
    Operator H = 1.0545718e-19 * Z + 2.6364295e-20 * X
    State prep = Evolve { prep under H for 0.35.fs }.run()
    State magnetization = expect(Z, prep)
    State viewed = Inspect(magnetization)
    Measure prep
}
"""

_PREPARE_01 = """
package t
pub fn main() -> Unit {
    State bit = Coin()
    State prep = Mix (bit) {
      0 -> |0>,
      else -> |1>,
    }
    Measure prep
}
"""


def test_when_ket_prepare_zero_and_plus_runs() -> None:
    result = _run(_PREPARE_PLUS)
    assert result.status == "succeeded", _hard(result.diagnostics)


def test_when_ket_prepare_computational_basis_runs() -> None:
    result = _run(_PREPARE_01)
    assert result.status == "succeeded", _hard(result.diagnostics)


if __name__ == "__main__":
    test_when_ket_prepare_computational_basis_runs()
    test_when_ket_prepare_zero_and_plus_runs()
    print("OK — LISS-0138")
