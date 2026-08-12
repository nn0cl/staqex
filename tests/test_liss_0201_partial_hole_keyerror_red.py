"""AT-TDD: LISS-0201 — partial-hole programs must not raise raw KeyError."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_source  # noqa: E402


def test_partial_pipe_no_keyerror() -> None:
    try:
        result = run_source(
            """
            package t
            fn second(x: State<Bit>, y: State<Bit>) -> State<Bit> {
                State x = |0>
                return y
            }
            pub fn main() -> Unit {
                State z = |0>
                State p = second(z, _)
                State w = |1>
                State r = w |> p
                measure r
            }
            """,
            stdout=io.StringIO(),
        )
    except KeyError as exc:
        raise AssertionError(f"raw KeyError escaped: {exc!r}") from exc
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1


def main() -> None:
    test_partial_pipe_no_keyerror()
    print("PASS test_partial_pipe_no_keyerror")
    print("OK - LISS-0201")


if __name__ == "__main__":
    main()
