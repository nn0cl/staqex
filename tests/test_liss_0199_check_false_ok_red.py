"""AT-TDD: LISS-0199 — `staqex check` must fail on hard compile diagnostics."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import cmd_check  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _args(source: str):
    ns = type("Args", (), {})()
    ns.expr = source
    ns.file = None
    ns.target = None
    ns.dag = False
    return ns


EFFECT_SRC = """
package t
fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
    return Inspect(x)
}
fn pure_wrapper(x: State<Float>) -> State<Float> {
    return inspect_state(x)
}
pub fn main() -> Unit {
    State psi = Dirac(0.0)
    State viewed = pure_wrapper(psi)
    Measure viewed
}
"""


def test_compile_rejects_effect_violation() -> None:
    compiled = compile_source(EFFECT_SRC)
    assert compiled.ok is False
    assert any(d.get("code") == "EFFECT_VIOLATION_ERROR" for d in compiled.diagnostics)


def test_check_exits_nonzero_on_effect_violation() -> None:
    buf = io.StringIO()
    err = io.StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = buf, err
        code = cmd_check(_args(EFFECT_SRC))
    finally:
        sys.stdout, sys.stderr = old_out, old_err
    assert code != 0, f"check must fail; stdout={buf.getvalue()!r} stderr={err.getvalue()!r}"
    assert "EFFECT_VIOLATION_ERROR" in err.getvalue()


def main() -> None:
    test_compile_rejects_effect_violation()
    print("PASS test_compile_rejects_effect_violation")
    test_check_exits_nonzero_on_effect_violation()
    print("PASS test_check_exits_nonzero_on_effect_violation")
    print("OK - LISS-0199")


if __name__ == "__main__":
    main()
