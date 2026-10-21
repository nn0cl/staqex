"""P02–P08 baseline observations through actual Parser methods, not a proposal."""

from dataclasses import fields, is_dataclass
from enum import Enum

from compiler.staqex.lexer import Lexer
from compiler.staqex.parser import Parser, ParseError

CALLBACKS = ("_span", "_match", "_check", "_advance", "_expect", "_peek",
             "_op_expression", "_ket_or_outer", "_comma_op_expr_items", "_algebra_call", "_op_binder")
PRIMARY_CASES = [
    "0", "17", "3.25", "((X))", "(X", "|0>", "|x><x|", "|x><y|",
    "[]", "[X]", "[X,Y]", "[X,Y,]", "[X,Y,Z]", "[X,Y", "[X,)]",
    "{}", "{X}", "{X,Y}", "{X,Y,}", "{X,Y,Z}", "{X,Y", "{X,)}",
    "P", "Q", "N", "P.a[0][1]", "Q(1)", "N[0].a",
    "hop(1,2)", "hop(1)", "hop(1,x)", "hop(1,2)(3)",
    "I", "X", "Y", "Z", "X()", "Y(0,1)", "Z[0][1]", "X.a",
    "a", "a.b.c[0][1]", "f()", "f(X,Y)", "f(X,)", "a[0].b", ";",
]
EXPRESSION_CASES = ["X+Y*Z", "(X+Y)*Z", "-X", "adjoint(X)", "[X,Y]", "{X,Y}"]
CASES = [("primary", s) for s in PRIMARY_CASES] + [("expression", s) for s in EXPRESSION_CASES]


def parser(source):
    tokens, diagnostics = Lexer(source).tokenize()
    assert not diagnostics, diagnostics
    return Parser(tokens)


def value(item):
    if is_dataclass(item):
        return {"type": type(item).__name__, **{f.name:value(getattr(item, f.name)) for f in fields(item)}}
    if isinstance(item, Enum):
        return item.name
    if isinstance(item, (tuple, list)):
        return [value(x) for x in item]
    if isinstance(item, dict):
        return {str(k):value(v) for k,v in item.items()}
    return item


def observe(kind, source):
    target = parser(source)
    tokens, diagnostics = target.tokens, target.diagnostics
    unrelated = object()
    target._test_unrelated = unrelated
    events = []
    for name in CALLBACKS:
        original = getattr(target, name)
        def traced(*args, _name=name, _original=original, **kwargs):
            events.append(_name)
            return _original(*args, **kwargs)
        setattr(target, name, traced)
    try:
        result = target._legacy_parse_operator_expression() if kind == "primary" else target._op_expression()
        outcome = {"result":value(result)}
    except ParseError as error:
        outcome = {"error":dict(type=type(error).__name__, args=value(error.args), **value(error.__dict__))}
    assert target.tokens is tokens and target.diagnostics is diagnostics
    assert target._test_unrelated is unrelated
    outcome.update(i=target.i, prev=value(target._prev), remaining=[t.lexeme for t in target.tokens[target.i:]],
                   diagnostics=value(target.diagnostics), events=events)
    return outcome
