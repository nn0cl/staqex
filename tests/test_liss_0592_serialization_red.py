"""R01–R04: real ParseError serialization; no substitute reducer or class."""

import base64
import copy
import inspect
import os
import pickle
import subprocess
import sys
from pathlib import Path

import pytest

from compiler.staqex.ast_nodes import OpLit, Span
from compiler.staqex.lexer import Lexer
from compiler.staqex.parser import ParseError, Parser
from compiler.staqex.tokens import TokenKind


ROOT = Path(__file__).resolve().parents[1]
PROTOCOLS = [None, *range(pickle.HIGHEST_PROTOCOL + 1)]


def assert_same_error(actual, expected):
    assert actual is not expected
    assert type(actual) is type(expected) is ParseError
    assert actual.__dict__ == expected.__dict__
    assert actual.args == expected.args
    assert str(actual) == str(expected)
    assert repr(actual) == repr(expected)


@pytest.mark.parametrize("protocol", PROTOCOLS)
@pytest.mark.parametrize("message", ["", "plain", "復元する", "line1\nline2"])
@pytest.mark.parametrize("code,line,col", [("PARSE_ERROR", 0, -1), ("CUSTOM", 4, 9)])
def test_r01_all_protocols_restore_actual_class_and_fields(protocol, message, code, line, col):
    original = ParseError(message, line, col, code=code)
    encoded = pickle.dumps(original, protocol=protocol)
    restored = pickle.loads(encoded)
    assert_same_error(restored, original)
    assert (restored.message, restored.line, restored.col, restored.code) == (message, line, col, code)
    assert original.args == (message,)


@pytest.mark.parametrize("protocol", PROTOCOLS)
def test_r03_pickle_preserves_extra_state_aliases_notes_and_independent_args(protocol):
    original = ParseError("message", 2, 3, code="CUSTOM")
    original.args = ("independent args", 7)
    metadata = {"items": [1, 2]}
    original.metadata = metadata
    original.alias = metadata
    original.owner = original
    original.add_note("first note")
    original.add_note("日本語")

    restored = pickle.loads(pickle.dumps(original, protocol=protocol))

    assert type(restored) is ParseError and restored is not original
    assert restored.args == original.args
    assert (restored.message, restored.line, restored.col, restored.code) == ("message", 2, 3, "CUSTOM")
    assert restored.metadata == metadata and restored.metadata is restored.alias
    assert restored.metadata is not metadata and restored.metadata["items"] is not metadata["items"]
    assert restored.owner is restored
    assert restored.__notes__ == ["first note", "日本語"]
    assert str(restored) == str(original) and repr(restored) == repr(original)
    assert original.owner is original and original.metadata is metadata
    assert original.args == ("independent args", 7)


@pytest.mark.parametrize("operation", [copy.copy, copy.deepcopy], ids=["shallow", "deep"])
def test_r03_copy_semantics_preserve_original_and_mutable_state(operation):
    original = ParseError("copy", 1, 2, code="CUSTOM")
    original.args = ("different", 8)
    original.metadata = {"items": [1]}
    original.alias = original.metadata
    original.add_note("note")
    restored = operation(original)
    assert_same_error(restored, original)
    assert restored.metadata is restored.alias
    if operation is copy.copy:
        assert restored.metadata is original.metadata
        assert restored.__notes__ is original.__notes__
    else:
        assert restored.metadata is not original.metadata
        assert restored.metadata["items"] is not original.metadata["items"]
        assert restored.__notes__ is not original.__notes__
    assert original.metadata == {"items": [1]} and original.args == ("different", 8)


@pytest.mark.parametrize("source,entry", [("X", "expect"), ("[X]", "primary"), ("{X}", "primary")])
@pytest.mark.parametrize("first", ["compiler.staqex.parser", "compiler.staqex.parsing.operators"])
def test_r02_real_raised_errors_round_trip_in_fresh_import_orders(source, entry, first):
    tokens, diagnostics = Lexer(source).tokenize()
    assert not diagnostics
    parser = Parser(tokens)
    with pytest.raises(ParseError) as caught:
        if entry == "expect":
            parser._expect(TokenKind.INT)
        else:
            parser._op_primary()
    original = caught.value
    encoded = base64.b64encode(pickle.dumps(original)).decode()
    expected = (original.message, original.line, original.col, original.code, original.args)
    program = f'''import importlib,base64,pickle
importlib.import_module({first!r})
from compiler.staqex.parser import ParseError
value=pickle.loads(base64.b64decode({encoded!r}))
assert type(value) is ParseError
assert (value.message,value.line,value.col,value.code,value.args)=={expected!r}
try:
    raise value
except ParseError as caught:
    assert caught is value
else:
    raise AssertionError("public exception catch failed")
'''
    result = subprocess.run([sys.executable, "-c", program], cwd=ROOT,
                            env={**os.environ, "PYTHONPATH": str(ROOT)},
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr


def test_r04_signature_fields_and_normal_raise_contract_stay_unchanged():
    parameters = inspect.signature(ParseError).parameters
    assert list(parameters) == ["message", "line", "col", "code"]
    for name in ("message", "line", "col"):
        assert parameters[name].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
        assert parameters[name].default is inspect.Parameter.empty
    assert parameters["code"].kind is inspect.Parameter.KEYWORD_ONLY
    assert parameters["code"].default == "PARSE_ERROR"
    for code in ("PARSE_ERROR", "CUSTOM"):
        value = ParseError("normal", 4, 5, code=code)
        assert value.args == ("normal",) and str(value) == "normal"
        assert repr(value) == "ParseError('normal')"
        assert value.__dict__ == dict(message="normal", line=4, col=5, code=code)
        with pytest.raises(ParseError) as caught:
            raise value
        assert caught.value is value


@pytest.mark.parametrize("args", [(), ("m",), ("m", 1), ("m", 1, 2, "code")])
def test_r04_invalid_constructor_calls_still_raise_typeerror(args):
    with pytest.raises(TypeError):
        ParseError(*args)


def test_r04_existing_ast_pickle_and_public_import_identities_survive():
    from compiler.staqex import modules, pipeline_legacy
    from compiler.staqex import parser as public
    assert modules.ParseError is pipeline_legacy.ParseError is ParseError
    value = OpLit(1.5, Span(2, 3))
    restored = pickle.loads(pickle.dumps(value))
    assert restored == value and type(restored) is OpLit
    assert public.OpLit is OpLit and public.Span is Span
