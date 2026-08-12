"""AT-TDD: LISS-0155 function partial `_` holes (ADR 0123)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_partial_typechecks_and_strict_arity() -> None:
    ok = compile_source(
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
        """
    )
    codes = {d.get("code", "") for d in ok.diagnostics}
    assert "PARSE_ERROR" not in codes, codes
    assert "FUNCTION_ARITY_ERROR" not in codes, codes
    assert "TYPE_NOT_STATE" not in codes, codes
    assert "PIPE_CALLABLE_ERROR" not in codes, codes

    bad = _codes(
        """
        package t
        fn second(x: State<Bit>, y: State<Bit>) -> State<Bit> {
            State x = |0>
            return y
        }
        pub fn main() -> Unit {
            State r = second(|0>)
            measure r
        }
        """
    )
    assert "FUNCTION_ARITY_ERROR" in bad


def test_partial_pipe_evaluates() -> None:
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
        stdout=__import__("io").StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1


if __name__ == "__main__":
    test_partial_typechecks_and_strict_arity()
    print("PASS test_partial_typechecks_and_strict_arity")
    test_partial_pipe_evaluates()
    print("PASS test_partial_pipe_evaluates")
