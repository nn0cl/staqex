"""AT-TDD: LISS-0358 -- method calls resolve a nested struct/class-field
receiver (`outer.inner.method()`), not just a bare Var.

Design decision: docs/issues/LISS-0358-nested-attr-receiver-dispatch.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source, run_source  # noqa: E402

_CLASSES = """
namespace Test {
    pub class Inner {
        var v: Float = 0.0
        fn init(x: Float) { this.v = x }
        pub fn get() -> Float { return this.v }
        pub fn h() -> Operator {
            Energy scale = 1.0.eV to J
            return scale * Z[0]
        }
    }
    pub class Outer {
        pub val inner: Test.Inner
        fn init(i: Test.Inner) { this.inner = i }
    }
}
"""


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def test_nested_receiver_state_bind() -> None:
    src = f"""
    {_CLASSES}
    Test.Inner i = Test.Inner(3.0)
    Test.Outer o = Test.Outer(i)
    Float nested = o.inner.get()
    State answer = Dirac(nested == 3.0)
    Measure answer
    """
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard, (result.status, hard)


def test_nested_receiver_embedded_in_classical_expression() -> None:
    src = f"""
    {_CLASSES}
    Test.Inner i = Test.Inner(3.0)
    Test.Outer o = Test.Outer(i)
    Float nested = o.inner.get() + 0.0
    State answer = Dirac(nested == 3.0)
    Measure answer
    """
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard, (result.status, hard)


def test_nested_receiver_operator_returning_method() -> None:
    src = f"""
    {_CLASSES}
    Test.Inner i = Test.Inner(1.0)
    Test.Outer o = Test.Outer(i)
    Operator H = o.inner.h()
    State s = |+>
    Time duration = 1.0.fs
    Operator U = exp(-i * H)
    State s = Evolve() {{ U * s }}.run()
    Measure s
    """
    compiled = compile_source(src)
    hard_compile = _hard(compiled.diagnostics)
    assert compiled.ok and not hard_compile, hard_compile


def test_single_level_receiver_still_works() -> None:
    """Regression guard: the already-supported bare-Var receiver case."""
    src = f"""
    {_CLASSES}
    Test.Inner i = Test.Inner(2.0)
    Float direct = i.get()
    Operator H = i.h()
    State s = |+>
    Time duration = 1.0.fs
    Operator U = exp(-i * H)
    State s = Evolve() {{ U * s }}.run()
    State answer = Dirac(direct == 2.0)
    Measure answer tracing_out s
    """
    compiled = compile_source(src)
    hard_compile = _hard(compiled.diagnostics)
    assert compiled.ok and not hard_compile, hard_compile
