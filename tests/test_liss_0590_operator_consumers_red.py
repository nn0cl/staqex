"""O06/O08 actual public/private consumers, imports, pickle and source paths."""

import importlib
import os
import pickle
import subprocess
import sys
import types

import pytest

from compiler.staqex.ast_nodes import OpBin, OpVar, Span
from compiler.staqex.pipeline import compile_source
from compiler.staqex.typecheck import TypeChecker, Ty
from compiler.staqex.typechecking.operators import check_operator_expr
from tests.liss_0590_guard_support import ROOT


def test_o06_public_entry_retains_custom_variadic_forwarding():
    marker = object()
    calls = []
    custom = types.SimpleNamespace(_legacy_check_operator=lambda *a, **kw: calls.append((a, kw)) or marker)
    assert check_operator_expr(custom, 1, 2, expr=3, extra=4) is marker
    assert calls == [((1, 2), dict(expr=3, extra=4))]


@pytest.mark.parametrize("name", ["_legacy_check_operator", "_check_operator_expr"])
def test_o06_real_unbound_self_keyword_and_plain_bound_pickle(name):
    checker = TypeChecker()
    expr = OpVar("x", Span(1, 2))
    assert getattr(TypeChecker, name)(self=checker, expr=expr) is None
    bound = pickle.loads(pickle.dumps(getattr(checker, name)))
    assert type(bound.__self__) is TypeChecker
    assert bound.__func__ is getattr(TypeChecker, name)
    assert bound(expr) is None
    value = Ty("Meta", "Index")
    assert type(pickle.loads(pickle.dumps(value))) is Ty


@pytest.mark.parametrize("kind", ["instance", "subclass"])
def test_o06_recursive_hooks_honor_live_overrides(kind):
    seen = []

    class Recording(TypeChecker):
        def _check_operator_expr(self, expr):
            seen.append(expr)

    checker = Recording() if kind == "subclass" else TypeChecker()
    if kind == "instance":
        checker._check_operator_expr = lambda expr: seen.append(expr)
    expr = OpBin("+", OpVar("a", Span(1, 1)), OpVar("b", Span(1, 2)), Span(1, 1))
    checker._legacy_check_operator(expr)
    assert seen == [expr.lhs, expr.rhs]
    assert check_operator_expr(TypeChecker(), OpVar("x", Span(1, 1))) is None


@pytest.mark.parametrize("first", ["compiler.staqex.typecheck", "compiler.staqex.typechecking.operators"])
def test_o06_cold_import_orders_pipeline_and_hir(first):
    code = f'''import importlib
importlib.import_module({first!r})
from compiler.staqex.typecheck import TypeChecker, Ty
from compiler.staqex.typechecking.operators import check_operator_expr
from compiler.staqex.ast_nodes import OpVar, Span
from compiler.staqex.pipeline import compile_source
from compiler.staqex import hir
assert check_operator_expr(TypeChecker(), OpVar("x", Span(1,1))) is None
result = compile_source("package t\\npub fn main() -> Unit {{\\n State q = |0>\\n Measure q\\n}}\\n")
assert result.ok, result.diagnostics
assert result.unit is not None
assert hir.Ty is Ty
'''
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT)}, capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("domain", ["Basis<2>", "rev(Basis<2>)", "0..1", "rev(0..1)"])
def test_o08_real_pipeline_binders_and_lowered_hir(domain):
    source = f'''package t
pub fn main() -> Unit {{
 QubitRegister<2> register = system()
 Operator H = Sigma (i In {domain}) {{ Z[i] }}
 State q = |0>
 Measure q
}}
'''
    result = compile_source(source)
    assert result.ok, result.diagnostics
    assert result.unit is not None
    assert result.qpu_ir["binder_lowering"]["H"]["expanded_terms"] == 2
