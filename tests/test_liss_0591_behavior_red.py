"""P02–P07 actual direct primary, callback timing and cursor contracts."""

import json
import types
from dataclasses import replace

import pytest

from compiler.staqex.ast_nodes import OpCall, OpLit
from compiler.staqex.parser import Parser
from compiler.staqex.tokens import Token, TokenKind
from tests import liss_0591_guard_support as guard
from tests.liss_0591_behavior_support import CASES, observe, parser


def observations():
    data = (guard.FIXTURES / "behavior.json").read_bytes()
    assert guard.sha(data) == "09c194415e48df2891f9cc36335a9f5939284d607acdeb72b306f64843fe237f"
    result = json.loads(data)
    assert result["base"] == guard.baseline()["base"]
    assert [(r["kind"], r["source"]) for r in result["cases"]] == CASES
    return result["cases"]


@pytest.mark.parametrize("index", range(len(CASES)), ids=[k+":"+s for k,s in CASES])
def test_p02_p05_exact_ast_span_errors_callback_order_cursor_and_remainder(index):
    row = observations()[index]
    assert observe(row["kind"], row["source"]) == row["expected"]


@pytest.mark.parametrize("name", ["Sigma", "Pi", "ForAll", "Min"])
def test_p04_all_binder_names_keep_live_callback_and_original_span(name):
    target = parser(name + "(unused)")
    result, calls = object(), []
    def binder(actual, span):
        calls.append((actual, span))
        return result
    target._op_binder = binder
    assert target._legacy_parse_operator_expression() is result
    assert len(calls) == 1 and calls[0][0] == name
    assert (calls[0][1].line, calls[0][1].col) == (1, 1)
    assert target.i == 1 and target._peek().kind is TokenKind.LPAREN


def test_p02_parenthesized_and_ket_helpers_return_exact_child_identity():
    for source, callback in [("(X)", "_op_expression"), ("|0>", "_ket_or_outer")]:
        target = parser(source)
        child, calls = object(), []
        def helper(*args):
            calls.append(args)
            if callback == "_op_expression":
                target._advance()
            return child
        setattr(target, callback, helper)
        assert target._legacy_parse_operator_expression() is child
        assert len(calls) == 1
        if callback == "_ket_or_outer":
            assert calls[0][0] is target.tokens[0]
            assert target.i == 1 and target._prev is target.tokens[0]


@pytest.mark.parametrize("source,closer", [("[X,Y]", TokenKind.RBRACKET), ("{X,Y}", TokenKind.RBRACE)])
def test_p03_items_list_and_span_identity_reach_algebra_after_helper(source, closer):
    target = parser(source)
    items, result, calls = [object(), object()], object(), []
    def children(actual):
        assert actual is closer
        calls.append("children")
        return items
    def algebra(name, actual_items, span):
        assert actual_items is items and (span.line, span.col) == (1, 1)
        assert name == ("commutator" if source[0] == "[" else "anticommutator")
        calls.append("algebra")
        return result
    target._comma_op_expr_items, target._algebra_call = children, algebra
    assert target._legacy_parse_operator_expression() is result
    assert calls == ["children", "algebra"]


FAILURE_SITES = [
    ("_span", "X"), ("_match", "X"), ("_check", "X"), ("_advance", "X"),
    ("_expect", "(X)"), ("_peek", "X"), ("_op_expression", "(X)"),
    ("_ket_or_outer", "|0>"), ("_comma_op_expr_items", "[X,Y]"),
    ("_algebra_call", "[X,Y]"), ("_op_binder", "Sigma"),
]


@pytest.mark.parametrize("callback,source", FAILURE_SITES)
@pytest.mark.parametrize("exception_type", [RuntimeError, KeyboardInterrupt])
def test_p07_all_eleven_callback_exceptions_propagate_without_cursor_or_state_rollback(callback, source, exception_type):
    target = parser(source)
    tokens, diagnostics, unrelated = target.tokens, target.diagnostics, object()
    target.unrelated = unrelated
    error = exception_type(callback)
    calls = []
    def failing(*args, **kwargs):
        calls.append((target.i, target._prev))
        raise error
    setattr(target, callback, failing)
    with pytest.raises(exception_type) as caught:
        target._legacy_parse_operator_expression()
    assert caught.value is error and len(calls) == 1
    assert (target.i, target._prev) == calls[0]
    assert target.tokens is tokens and target.diagnostics is diagnostics
    assert diagnostics == [] and target.unrelated is unrelated


@pytest.mark.parametrize("kind", [TokenKind.INT, TokenKind.FLOAT])
def test_p07_float_conversion_failure_is_after_advance_and_not_caught(kind):
    error = ValueError("float-conversion")
    class Bad:
        def __float__(self):
            raise error
    target = Parser([Token(kind, "bad", 2, 3, Bad()), Token(TokenKind.EOF, "", 2, 6)])
    with pytest.raises(ValueError) as caught:
        target._legacy_parse_operator_expression()
    assert caught.value is error and target.i == 1 and target._prev is target.tokens[0]


@pytest.mark.parametrize("invocation", ["bound", "class", "unbound-keyword", "primary"])
def test_p07_receiver_forms_share_actual_instance_and_state(invocation):
    target = parser("17")
    if invocation == "bound":
        result = target._legacy_parse_operator_expression()
    elif invocation == "class":
        result = Parser._legacy_parse_operator_expression(target)
    elif invocation == "unbound-keyword":
        result = Parser._legacy_parse_operator_expression(self=target)
    else:
        result = target._op_primary()
    assert isinstance(result, OpLit) and result.value == 17.0
    assert target.i == 1 and target._prev is target.tokens[0]


def test_p05_postfix_dagger_at_token_boundary_keeps_repeated_adjoint():
    # TokenKind.DAGGER exists at this parser boundary; Unicode lexer spelling
    # is not assumed to be accepted by the current language front end.
    target = Parser([Token(TokenKind.IDENT, "X", 1, 1), Token(TokenKind.DAGGER, "†", 1, 2),
                     Token(TokenKind.DAGGER, "†", 1, 3), Token(TokenKind.EOF, "", 1, 4)])
    result = target._op_expression()
    assert isinstance(result, OpCall) and result.name == "adjoint"
    assert isinstance(result.args[0], OpCall) and result.args[0].name == "adjoint"
    assert target.i == 3


def test_p07_recursive_primary_uses_live_override():
    target = parser("((X))")
    original = target._op_primary
    calls = []
    def live(self):
        calls.append(self.i)
        return original()
    target._op_primary = types.MethodType(live, target)
    result = target._legacy_parse_operator_expression()
    assert result.kind == "X" and calls == [1, 2]


@pytest.mark.parametrize("position", [2, 4])
def test_p07_hop_integer_conversion_failure_consumes_original_arguments_first(position):
    error = ValueError("int-conversion")
    class Bad:
        def __int__(self):
            raise error
    target = parser("hop(1,2)")
    target.tokens[position] = replace(target.tokens[position], literal=Bad())
    with pytest.raises(ValueError) as caught:
        target._legacy_parse_operator_expression()
    assert caught.value is error and target.i == 6
    assert target._prev is target.tokens[5]
