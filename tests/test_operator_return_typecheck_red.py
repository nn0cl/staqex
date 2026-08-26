"""Acceptance tests for the Operator-typed return typecheck gap (LISS-0048).

Reproduces the gap recorded in
docs/issues/LISS-0048-operator-return-typecheck-gap.md: a function that
binds an Operator-typed local and returns it under a mismatched declared
return type is not diagnosed by the typechecker and crashes the evaluator
with an unhandled KeyError instead.
"""

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


_MISMATCHED_OPERATOR_RETURN = """
fn bad() -> State<Int> {
    Operator k = X
    return k
}

pub fn main() -> Unit {
    State<Int> r = bad()
    Measure r
}
"""

_OPERATOR_DECLARED_RETURN = """
fn make_coin() -> Operator {
    Operator k = X
    return k
}

pub fn main() -> Unit {
    State<Int> r = Dirac(0)
    Measure r
}
"""


def test_operator_local_return_type_mismatch_is_diagnosed() -> None:
    codes = _codes(_MISMATCHED_OPERATOR_RETURN)

    assert "RETURN_TYPE_MISMATCH" in codes


def test_operator_local_return_type_mismatch_does_not_crash_at_runtime() -> None:
    result = run_source(_MISMATCHED_OPERATOR_RETURN, seed=0, stdout=io.StringIO())

    assert result.compile_ok is False


def test_operator_return_under_operator_declared_type_still_works() -> None:
    codes = _codes(_OPERATOR_DECLARED_RETURN)
    assert "RETURN_TYPE_MISMATCH" not in codes

    result = run_source(_OPERATOR_DECLARED_RETURN, seed=0, stdout=io.StringIO())
    assert result.compile_ok is True


if __name__ == "__main__":
    tests = [
        test_operator_local_return_type_mismatch_is_diagnosed,
        test_operator_local_return_type_mismatch_does_not_crash_at_runtime,
        test_operator_return_under_operator_declared_type_still_works,
    ]
    for test in tests:
        test()
    print("OK — operator return typecheck tests")
