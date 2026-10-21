"""P01/P06 structural Red; P08/P10 preservation on actual production."""

import ast
import importlib
import subprocess

import pytest

from compiler.staqex.parser import Parser, ParseError
from tests import liss_0591_guard_support as guard
from tests.liss_0591_behavior_support import parser


def test_p01_sole_successor_owns_original_algorithm_and_declaration_context():
    guard.assert_successor(guard.ROOT)


def test_p01_facade_body_removed_exact_alias_factory_and_raw_inverse():
    tree = ast.parse((guard.ROOT / guard.PARSER).read_bytes())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Parser")
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "_legacy_parse_operator_expression" for n in cls.body), "primary body still owned by Parser"
    assert guard.installed((guard.ROOT / guard.PARSER).read_bytes())
    assert guard.sha(guard.parser_bytes(guard.ROOT)) == guard.baseline()["parser_sha256"]


def test_p06_both_actual_hooks_are_ordinary_bound_sole_successor():
    module = importlib.import_module("compiler.staqex.parsing.operators")
    algorithm = getattr(module, "_legacy_parse_operator_expression", None)
    assert callable(algorithm), "primary algorithm not extracted"
    target = parser("X")
    for name in ("_legacy_parse_operator_expression", "_op_primary"):
        assert getattr(Parser, name) is algorithm
        assert getattr(target, name).__self__ is target
        assert getattr(target, name).__func__ is algorithm
    assert algorithm is not module.parse_operator_expression


def test_p06_static_fresh_factory_all_three_real_sites_and_failure_controls(monkeypatch):
    factory = Parser.__dict__.get("_operator_parse_error")
    assert isinstance(factory, staticmethod), "static fresh ParseError factory missing"
    a, b = factory.__func__("m", 3, 7), factory.__func__("m", 3, 7)
    assert type(a) is type(b) is ParseError and a is not b
    assert (a.message, a.line, a.col, a.code, a.args) == ("m", 3, 7, "PARSE_ERROR", ("m",))
    calls = []
    def recording(*args):
        calls.append(args)
        return factory.__func__(*args)
    monkeypatch.setattr(Parser, "_operator_parse_error", staticmethod(recording))
    for source in ("[X]", "{X}", ";"):
        calls.clear()
        with pytest.raises(ParseError) as caught:
            parser(source)._legacy_parse_operator_expression()
        assert calls == [(caught.value.message, caught.value.line, caught.value.col)]
        assert caught.value.__traceback__.tb_next.tb_frame.f_code is Parser._legacy_parse_operator_expression.__code__
    for error in (RuntimeError("factory"), KeyboardInterrupt("factory")):
        calls.clear()
        def failing(*args):
            calls.append(args)
            raise error
        monkeypatch.setattr(Parser, "_operator_parse_error", staticmethod(failing))
        for source in ("[X]", "{X}", ";"):
            calls.clear()
            target = parser(source)
            with pytest.raises(type(error)) as caught:
                target._legacy_parse_operator_expression()
            assert caught.value is error and len(calls) == 1
        calls.clear()
        with pytest.raises(ParseError):
            parser("[X,Y")._legacy_parse_operator_expression()
        assert not calls, "earlier _expect error must not masquerade as factory coverage"
        parser("[X,Y]")._legacy_parse_operator_expression()
        assert not calls, "successful parse must not invoke error factory"


def test_p10_unrelated_production_and_all_six_carriers_keep_frozen_bytes():
    assert guard.sha(guard.parser_bytes(guard.ROOT)) == guard.baseline()["parser_sha256"]
    assert guard.readonly_bytes(guard.ROOT, guard.OPERATORS) == guard.evidence("original-operators.txt")
    for path, expected in guard.baseline()["readonly_sha256"].items():
        assert guard.sha((guard.ROOT / path).read_bytes()) == expected, path
    paths = set(subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', 'compiler'], cwd=guard.ROOT, text=True).splitlines())
    guard.production_paths(guard.ROOT, paths)
    guard.assert_carriers()
    guard.historical_test_paths(guard.baseline()["test_paths"])


def test_b06_pure_inverse_has_no_project_import_or_executable_proposal():
    tree = ast.parse((guard.ROOT / "tests/liss_0591_guard_support.py").read_bytes())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            assert node.level == 0 and not node.module.startswith(("tests", "compiler"))
        if isinstance(node, ast.Import):
            assert all(not n.name.startswith(("tests", "compiler")) for n in node.names)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"exec", "eval", "compile"}
