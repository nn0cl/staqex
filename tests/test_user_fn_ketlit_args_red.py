"""AT-TDD: LISS-0162 user-fn State-forming Call args (ADR 0130)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def test_ketlit_direct_fn_arg() -> None:
    codes = {
        d.get("code", "")
        for d in compile_source(
            """
            package t
            fn id(x: State<Bit>) -> State<Bit> {
                return x
            }
            pub fn main() -> Unit {
                State r = id(|1>)
                Measure r
            }
            """
        ).diagnostics
    }
    assert "PARSE_ERROR" not in codes, codes
    assert "FUNCTION_ARITY_ERROR" not in codes, codes

    result = run_source(
        """
        package t
        fn id(x: State<Bit>) -> State<Bit> {
            return x
        }
        pub fn main() -> Unit {
            State r = id(|1>)
            Measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1


def test_partial_with_ketlit_bound_slot() -> None:
    result = run_source(
        """
        package t
        fn second(x: State<Bit>, y: State<Bit>) -> State<Bit> {
            State x = |0>
            return y
        }
        pub fn main() -> Unit {
            State p = second(|0>, _)
            State w = |1>
            State r = w |> p
            Measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1


if __name__ == "__main__":
    test_ketlit_direct_fn_arg()
    print("PASS test_ketlit_direct_fn_arg")
    test_partial_with_ketlit_bound_slot()
    print("PASS test_partial_with_ketlit_bound_slot")
