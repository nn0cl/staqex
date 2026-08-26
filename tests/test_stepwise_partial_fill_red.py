"""AT-TDD: LISS-0163 stepwise Partial fill (ADR 0131)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_stepwise_partial_typechecks_and_runs() -> None:
    src = """
    package t
    fn third(x: State<Bit>, y: State<Bit>, z: State<Bit>) -> State<Bit> {
        State x = |0>
        State y = |0>
        return z
    }
    pub fn main() -> Unit {
        State p2 = third(|0>, _, _)
        State p1 = p2(|1>)
        State w = |0>
        State r = w |> p1
        Measure r
    }
    """
    codes = _codes(src)
    assert "PARSE_ERROR" not in codes, codes
    assert "FUNCTION_ARITY_ERROR" not in codes, codes
    assert "TYPE_NOT_STATE" not in codes, codes

    result = run_source(src, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 0


def test_over_arity_partial_call_rejected() -> None:
    codes = _codes(
        """
        package t
        fn second(x: State<Bit>, y: State<Bit>) -> State<Bit> {
            return y
        }
        pub fn main() -> Unit {
            State p = second(|0>, _)
            State r = p(|1>, |0>)
            Measure r
        }
        """
    )
    assert "FUNCTION_ARITY_ERROR" in codes


if __name__ == "__main__":
    test_stepwise_partial_typechecks_and_runs()
    print("PASS test_stepwise_partial_typechecks_and_runs")
    test_over_arity_partial_call_rejected()
    print("PASS test_over_arity_partial_call_rejected")
