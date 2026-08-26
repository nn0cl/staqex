"""AT-TDD: LISS-0353 -- add an execution path for free functions that
return a struct type (LISS-0338's documented, deferred "Related, not
blocking" gap).

Design decision: docs/issues/LISS-0353-struct-returning-free-function-execution-path.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source, run_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def _run(src: str):
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)


def test_positional_struct_construction_inside_a_free_function_body() -> None:
    _run(
        """
        struct Point {
            val x: Float
            val y: Float
        }

        fn make_point(a: Float, b: Float) -> Point {
            return Point(a, b)
        }

        pub fn main() -> Unit {
            Point p = make_point(1.0, 2.0)
            Float sum = p.x + p.y
            State s = |0>
            Measure s
        }
        """
    )


def test_kwargs_struct_construction_inside_a_free_function_body() -> None:
    _run(
        """
        struct Point {
            val x: Float
            val y: Float
        }

        fn make_point_kw(a: Float, b: Float) -> Point {
            return Point { x: a, y: b }
        }

        pub fn main() -> Unit {
            Point p = make_point_kw(3.0, 4.0)
            Float sum = p.x + p.y
            State s = |0>
            Measure s
        }
        """
    )


def test_struct_returning_call_nested_as_an_argument() -> None:
    _run(
        """
        struct Point {
            val x: Float
            val y: Float
        }

        fn make_point(a: Float, b: Float) -> Point {
            return Point(a, b)
        }

        fn point_sum(p: Point) -> Float {
            return p.x + p.y
        }

        pub fn main() -> Unit {
            Float total = point_sum(make_point(5.0, 6.0))
            State s = |0>
            Measure s
        }
        """
    )
