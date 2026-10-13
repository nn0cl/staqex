"""C01–C05/C07: existing classification, live owner and recursive hooks."""

import copy

import pytest

from compiler.staqex.ast_nodes import (
    Attr, BinOp, Call, Coin, Dirac, LitBool, LitFloat, LitInt, LitString,
    Span, TupleExpr, UnaryNot, UnitConvert, Var,
)
from compiler.staqex import dimensions
from compiler.staqex.runtime.evaluator import Evaluator

S = Span(1, 2)


def context():
    owner = Evaluator.__new__(Evaluator)
    owner.scalars = {}
    owner.objects = {}
    return owner


class ExplodingMap:
    def __contains__(self, key):
        raise RuntimeError('membership read')


@pytest.mark.parametrize('expr,expected', [
    (LitInt(0, S), True), (LitFloat(0.0, S), True),
    (LitBool(False, S), True), (LitString('', S), True),
    (Call(Var('f', S), [LitInt(1, S)], S), False),
    (TupleExpr([LitInt(1, S)], S), False),
    (UnaryNot(LitBool(True, S), S), False),
    (Dirac(LitInt(1, S), S), False), (Coin(S), False),
])
def test_c01_literals_and_unsupported_nodes_do_not_read_or_descend(expr, expected):
    owner = context()
    owner.scalars = owner.objects = ExplodingMap()
    assert owner._is_closed(expr) is expected


@pytest.mark.parametrize('value', [False, 0, 0.0, None, object()])
def test_c02_membership_not_value_truth_or_type(value):
    owner = context()
    owner.scalars['x'] = value
    owner.objects['object_only'] = value
    assert owner._is_closed(Var('x', S)) is True
    assert owner._is_closed(Var('object_only', S)) is False
    assert owner._is_closed(Var('missing', S)) is False


def test_c02_c05_live_mutation_replacement_and_owner_isolation():
    owner, other = context(), context()
    scalar = Var('x', S)
    attr = Attr(Var('obj', S), 'nonexistent', S)
    for store, key, expr in [('scalars', 'x', scalar), ('objects', 'obj', attr)]:
        assert owner._is_closed(expr) is False
        mapping = getattr(owner, store)
        mapping[key] = None
        assert owner._is_closed(expr) is True
        assert other._is_closed(expr) is False
        del mapping[key]
        assert owner._is_closed(expr) is False
        setattr(owner, store, {key: False})
        assert owner._is_closed(expr) is True
        setattr(owner, store, {})
        assert owner._is_closed(expr) is False


@pytest.mark.parametrize('alias', ['pi', 'sqrt2', 'inv_sqrt2'])
def test_c03_math_aliases_win_before_environment_reads(alias):
    owner = context()
    owner.scalars = owner.objects = ExplodingMap()
    assert owner._is_closed(Attr(Var('Math', S), alias, S)) is True


@pytest.mark.parametrize('registered', [False, True])
def test_c03_registered_math_and_object_fields_do_not_validate_fields(registered):
    owner = context()
    if registered:
        owner.objects = {'Math': object(), 'obj': object()}
    for name in ['Math', 'obj']:
        assert owner._is_closed(Attr(Var(name, S), 'absent_field', S)) is registered


@pytest.mark.parametrize('receiver,name,expected', [
    (LitInt(1, S), 'm', True), (LitFloat(1.0, S), 'm', True),
    (LitInt(1, S), 'unknown_unit', False), (LitFloat(1.0, S), 'unknown_unit', False),
    (LitBool(True, S), 'm', False), (LitString('1', S), 'm', False),
    (Attr(Var('obj', S), 'x', S), 'm', False),
])
def test_c03_numeric_unit_membership_only(receiver, name, expected):
    owner = context()
    owner.objects['obj'] = object()
    assert owner._is_closed(Attr(receiver, name, S)) is expected


def test_c03_c07_unit_table_is_live_and_access_is_branch_lazy(monkeypatch):
    owner = context()
    monkeypatch.setattr(dimensions, 'UNIT_TABLE', ExplodingMap())
    assert owner._is_closed(LitInt(1, S)) is True
    assert owner._is_closed(Attr(Var('Math', S), 'pi', S)) is True
    with pytest.raises(RuntimeError, match='membership read'):
        owner._is_closed(Attr(LitInt(1, S), 'm', S))
    table = {}
    monkeypatch.setattr(dimensions, 'UNIT_TABLE', table)
    expr = Attr(LitFloat(3.0, S), 'added', S)
    assert owner._is_closed(expr) is False
    table['added'] = None
    assert owner._is_closed(expr) is True
    monkeypatch.setattr(dimensions, 'UNIT_TABLE', {})
    assert owner._is_closed(expr) is False


@pytest.mark.parametrize('op', ['+', '/', 'unsupported-op'])
def test_c04_nested_recursion_and_operator_spelling(op):
    owner = context()
    expr = UnitConvert(BinOp(op, LitInt(1, S), LitFloat(2.0, S), S), 'invalid-target', S)
    assert owner._is_closed(expr) is True
    expr.expr.rhs = Var('missing', S)
    assert owner._is_closed(expr) is False


@pytest.mark.parametrize('lhs_result', [False, True])
def test_c04_c05_instance_hook_order_short_circuit_and_exact_return(lhs_result):
    owner = context()
    lhs, rhs = Var('left', S), Var('right', S)
    calls = []
    sentinel = object()

    def hook(expr):
        calls.append(expr)
        if expr is lhs:
            return lhs_result
        assert expr is rhs
        if not lhs_result:
            raise AssertionError('rhs must be skipped')
        return sentinel

    owner._is_closed = hook
    assert Evaluator._is_closed(owner, BinOp('+', lhs, rhs, S)) is (sentinel if lhs_result else False)
    assert calls == ([lhs, rhs] if lhs_result else [lhs])
    calls.clear()
    def conversion_hook(expr):
        calls.append(expr)
        assert expr is rhs
        return sentinel
    owner._is_closed = conversion_hook
    assert Evaluator._is_closed(owner, UnitConvert(rhs, 'invalid', S)) is sentinel
    assert calls == [rhs]


def test_c04_subclass_recursion_and_hook_errors_propagate():
    seen = []

    class Override(Evaluator):
        def _is_closed(self, expr):
            seen.append(expr)
            if isinstance(expr, Var):
                raise LookupError('override child')
            return super()._is_closed(expr)

    owner = Override.__new__(Override)
    child = Var('x', S)
    root = UnitConvert(child, 'invalid', S)
    with pytest.raises(LookupError, match='override child'):
        owner._is_closed(root)
    assert seen == [root, child]


@pytest.mark.parametrize('expr,store', [(Var('x', S), 'scalars'), (Attr(Var('x', S), 'field', S), 'objects')])
def test_c04_membership_errors_propagate(expr, store):
    owner = context()
    setattr(owner, store, ExplodingMap())
    with pytest.raises(RuntimeError, match='membership read'):
        owner._is_closed(expr)


def test_c05_no_expression_state_or_joint_mutation_and_no_evaluation():
    owner = context()
    owner.scalars['x'] = object()
    owner.objects['obj'] = object()
    owner.joint = object()
    expr = BinOp('+', Var('x', S), Attr(Var('obj', S), 'field', S), S)
    original_expr = copy.deepcopy(expr)
    original_state = dict(vars(owner))
    scalars, objects = dict(owner.scalars), dict(owner.objects)
    assert owner._is_closed(expr) is True
    assert expr == original_expr
    assert vars(owner) == original_state
    assert owner.scalars == scalars and owner.objects == objects
    assert owner._is_closed.__self__ is owner
