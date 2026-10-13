"""C06 actual execution, Dirac binding and Operator factory consumers."""

import io
import sys
import types

import pytest

from compiler.staqex.ast_nodes import Call, Dirac, LitInt, Span, Var
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator
from compiler.staqex.runtime.evaluation.binding import bind
from compiler.staqex.runtime.evaluation.execution import execute_legacy_ast_body
from compiler.staqex.runtime.evaluation.operators import resolve_operator_factory_call
from compiler.staqex.runtime.joint import Joint

S = Span(1, 1)


def recording_hook(owner):
    calls = []
    original = Evaluator._is_closed

    def record(self, expr):
        caller = sys._getframe(1)
        calls.append((caller.f_code.co_filename, caller.f_lineno, expr))
        return original(self, expr)

    owner._is_closed = types.MethodType(record, owner)
    return calls


def test_c06_actual_execution_single_tuple_capture_and_dirac():
    compiled = compile_source('''package t
pub fn main() -> Unit {
    Float a = 2.0
    b, c = 3.0, 4.0
    State s = Dirac(a + b + c)
    Measure s
}
''')
    assert compiled.unit is not None, compiled.diagnostics
    owner = Evaluator(seed=0)
    calls = recording_hook(owner)
    # Characterize the actual shell sites, not an optimized alternate route.
    owner._main_interproc_trace_eligible = lambda stmts: False
    owner._main_deferred_eligible = lambda stmts: False
    result = execute_legacy_ast_body(owner, compiled.unit, stdout=io.StringIO())
    assert result.measure.value == 9.0
    assert {name: owner.scalars[name] for name in ('a', 'b', 'c')} == {'a': 2.0, 'b': 3.0, 'c': 4.0}
    assert {313, 342} <= {line for path, line, _ in calls if path.endswith('/evaluation/execution.py')}
    assert any(path.endswith('/evaluation/binding.py') and line == 168 for path, line, _ in calls)


@pytest.mark.parametrize('closed', [False, True])
def test_c06_actual_dirac_constant_and_pushforward_paths(closed):
    owner = Evaluator.__new__(Evaluator)
    owner.scalars = {'q': None} if closed else {}
    owner.objects = {}
    calls = recording_hook(owner)
    evaluated = []

    def evaluate(expr, assign):
        evaluated.append((expr, dict(assign)))
        return assign['q'] if assign else 7

    owner._evaluate_nested_value = evaluate
    expr = Var('q', S)
    joint = Joint.unit().bind_const('q', 2)
    result = bind(owner, joint, 'out', Dirac(expr, S))
    assert result.marginal('out') == {(7 if closed else 2): 1.0}
    assert evaluated == [(expr, {} if closed else {'q': 2})]
    assert joint.marginal('q') == {2: 1.0}
    assert any(path.endswith('/evaluation/binding.py') and line == 168 for path, line, _ in calls)


@pytest.mark.parametrize('local_object', [False, True])
def test_c06_actual_factory_scalar_and_local_object_fallback(local_object):
    if local_object:
        source = '''package t
struct Coeff { val value: Float }
fn make(c: Coeff) -> Operator {
    Float x = c.value
    return x * Z[0]
}
pub fn main() -> Unit { Measure |0> }
'''
    else:
        source = '''package t
fn make() -> Operator {
    Float x = 2.0
    return x * Z[0]
}
pub fn main() -> Unit { Measure |0> }
'''
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    owner = Evaluator(seed=0)
    # Initialize the real environment using the actual shell.
    execute_legacy_ast_body(owner, compiled.unit, stdout=io.StringIO())
    calls = recording_hook(owner)
    args = []
    if local_object:
        owner.objects['outer'] = owner._make_struct_value('Coeff', {'value': 2.0}, {})
        args = [Var('outer', S)]
    fun = next(d for d in compiled.unit.decls if getattr(d, 'name', None) == 'make')
    result = resolve_operator_factory_call(owner, Call(Var('make', S), args, S), fun)
    assert result is not None
    assert any(path.endswith('/evaluation/operators.py') and line == 454 for path, line, _ in calls)
    assert 'x' not in owner.scalars
    if local_object:
        # Predicate itself rejects the parameter name; the consumer's explicit
        # local-object fallback must remain effective without changing closure.
        attr = next(expr for path, line, expr in calls if path.endswith('/evaluation/operators.py') and line == 454)
        assert Evaluator._is_closed(owner, attr) is False
