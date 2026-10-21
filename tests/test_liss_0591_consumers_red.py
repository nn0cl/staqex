"""P05/P06/P08 real consumers, exports, forwarding and serialization."""

import copy
import importlib
import pickle
import subprocess
import sys

import pytest

from compiler.staqex.ast_nodes import OpLit, Span
from compiler.staqex.parser import Parser, ParseError
from compiler.staqex.parsing.operators import parse_operator_expression
from tests import liss_0591_guard_support as guard
from tests import test_liss_0592_consumers_red as retained
from tests.liss_0592_consumer_support import CASES


@pytest.mark.parametrize("kind,name", CASES)
def test_p08_actual_pipeline_module_access_nested_parser_consumers(tmp_path, kind, name):
    retained.test_r05_real_consumer_status_and_exact_ordered_diagnostics(tmp_path, kind, name)


def test_p06_public_variadic_forwarding_uses_live_custom_callback_and_exceptions():
    calls, result = [], object()
    class Context:
        def _legacy_parse_operator_expression(self, *args, **kwargs):
            calls.append((args, kwargs))
            return result
    context = Context()
    marker = object()
    assert parse_operator_expression(context, marker, named=marker) is result
    assert calls == [((marker,), {"named":marker})]
    for error in (RuntimeError("callback"), KeyboardInterrupt("callback")):
        def failing(*args, **kwargs):
            raise error
        context._legacy_parse_operator_expression = failing
        with pytest.raises(type(error)) as caught:
            parse_operator_expression(context, marker, named=marker)
        assert caught.value is error


def test_p08_all_original_public_exports_and_reexport_identity():
    facade = importlib.import_module("compiler.staqex.parser")
    for name, names in guard.baseline()["exports"].items():
        module = importlib.import_module(name)
        actual = set(module.__all__ if hasattr(module, "__all__") else [n for n in vars(module) if not n.startswith('_')])
        assert set(names) == actual, name
        for symbol in names:
            assert hasattr(module, symbol)
    for name in ("compiler.staqex.pipeline_legacy", "compiler.staqex.modules"):
        module = importlib.import_module(name)
        assert module.Parser is Parser and module.ParseError is ParseError
    assert facade.Token is importlib.import_module("compiler.staqex.tokens").Token
    assert facade.OpLit is OpLit


@pytest.mark.parametrize("protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_p08_ast_and_actual_repaired_parseerror_roundtrip(protocol):
    original = OpLit(value=2.5, span=Span(3, 7))
    restored = pickle.loads(pickle.dumps(original, protocol))
    assert type(restored) is OpLit and restored == original
    error = ParseError("message", 3, 7)
    error.args = ("independent", 99)
    error.notes = ["meta"]
    restored = pickle.loads(pickle.dumps(error, protocol))
    assert type(restored) is ParseError and restored.__dict__ == error.__dict__
    assert restored.args == error.args
    assert copy.copy(error).notes is error.notes
    assert copy.deepcopy(error).notes == error.notes and copy.deepcopy(error).notes is not error.notes


@pytest.mark.parametrize("order", [
    ["compiler.staqex.parser", "compiler.staqex.parsing.operators", "compiler.staqex.pipeline_legacy", "compiler.staqex.modules", "compiler.staqex.access"],
    ["compiler.staqex.parsing.operators", "compiler.staqex.modules", "compiler.staqex.access", "compiler.staqex.pipeline_legacy", "compiler.staqex.parser"],
])
def test_p08_two_requested_cold_import_orders(order):
    script = ('import importlib,pickle; '
              + '; '.join('importlib.import_module(%r)' % n for n in order)
              + '; from compiler.staqex.parser import Parser,ParseError; '
              + 'from compiler.staqex import modules,pipeline_legacy; '
              + 'assert modules.Parser is pipeline_legacy.Parser is Parser; '
              + 'e=ParseError("cold",2,4); r=pickle.loads(pickle.dumps(e)); '
              + 'assert type(r) is ParseError and (r.line,r.col)==(2,4)')
    result = subprocess.run([sys.executable, '-c', script], cwd=guard.ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_p05_real_parse_and_compile_adjacent_operator_binder_families():
    from tests import test_operator_pauli_atom_call_parse_red as pauli
    from tests import test_binder_body_operator_expression_red as binder
    pauli.test_indexed_pauli_atom_parses_as_op_indexed()
    pauli.test_indexed_pauli_product_parses_as_op_bin()
    pauli.test_hop_call_parses_as_op_hop()
    # Existing accepted tests remain authoritative and execute their real
    # Parser/compile pipeline, including where/Implies and reserved factories.
    for name in sorted(n for n in vars(binder) if n.startswith("test_")):
        getattr(binder, name)()


def test_e01_e06_actual_operator_wildcard_exports_keep_exact_names_and_identity():
    # Exercise the installed package in a fresh process, never an AST-only root.
    script = '''
import __future__
from typing import Any
from compiler.staqex.parsing import operators, parse_operator_expression
from compiler.staqex.parsing.context import ParserContext

namespace = {}
exec("from compiler.staqex.parsing.operators import *", namespace)
actual = set(namespace) - {"__builtins__"}
assert actual == set(%r), (actual, "operator wildcard exports changed")
originals = {
    "Any": Any,
    "ParserContext": ParserContext,
    "annotations": __future__.annotations,
    "parse_operator_expression": parse_operator_expression,
}
for name, original in originals.items():
    assert namespace[name] is original, name
    assert getattr(operators, name) is original, name
''' % guard.baseline()["exports"]["compiler.staqex.parsing.operators"]
    result = subprocess.run([sys.executable, '-c', script], cwd=guard.ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
