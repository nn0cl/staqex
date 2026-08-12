"""AT-TDD: LISS-0154 pipeline unary bare stage (ADR 0122)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_unary_bare_pipe_typechecks() -> None:
    compiled = compile_source(
        """
        package t
        fn id(x: State<Bit>) -> State<Bit> {
            return x
        }
        pub fn main() -> Unit {
            State a = |0>
            State a = a |> id
            measure a
        }
        """
    )
    codes = {d.get("code", "") for d in compiled.diagnostics}
    assert "PIPE_CALLABLE_ERROR" not in codes, codes
    assert "PARSE_ERROR" not in codes, codes
    assert "FUNCTION_ARITY_ERROR" not in codes, codes
    assert "MISSING_RETURN_STATEMENT" not in codes, codes


def test_operator_bare_pipe_rejected() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            Operator H = X
            State result = psi |> H
            measure result
        }
        """
    )
    assert "PIPE_CALLABLE_ERROR" in codes


if __name__ == "__main__":
    test_unary_bare_pipe_typechecks()
    print("PASS test_unary_bare_pipe_typechecks")
    test_operator_bare_pipe_rejected()
    print("PASS test_operator_bare_pipe_rejected")
