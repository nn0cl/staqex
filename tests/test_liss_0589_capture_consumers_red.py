"""S06 actual shell/observation calls, override dispatch and source regressions."""

import io
import ast
from pathlib import Path
import sys
import types

import pytest

from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator
from compiler.staqex.runtime.evaluation.execution import execute_legacy_ast_body
from compiler.staqex.runtime.evaluation import execution
from compiler.staqex.runtime.evaluation.observation import (
    _prepare_first_family_context, _run_deferred_state_binds,
)
from compiler.staqex.runtime.joint import Joint
from tests.test_classical_float_operator_evolve_binding_red import (
    _EVOLVE_FOR_METHOD_FLOAT, _FIELD_TO_FLOAT,
)


def record(owner, joint, name, caller):
    owner.capture_calls.append((caller.f_code.co_filename, name))
    return Evaluator._maybe_capture_classical_scalar(owner, joint, name)


class RecordingEvaluator(Evaluator):
    def _maybe_capture_classical_scalar(self, joint, name):
        return record(self, joint, name, sys._getframe(1))


def recording_owner(kind):
    owner = (RecordingEvaluator if kind == 'subclass' else Evaluator)(seed=0)
    owner.capture_calls = []
    if kind == 'instance':
        def hook(self, joint, name):
            return record(self, joint, name, sys._getframe(1))
        owner._maybe_capture_classical_scalar = types.MethodType(hook, owner)
    return owner


@pytest.mark.parametrize('kind', ['instance', 'subclass'])
@pytest.mark.parametrize('source,name', [
    (_EVOLVE_FOR_METHOD_FLOAT, 'duration'), (_FIELD_TO_FLOAT, 'J'),
])
def test_s06_real_execution_method_duration_and_field_coefficient(kind, source, name):
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    owner = recording_owner(kind)
    owner._main_interproc_trace_eligible = lambda stmts: False
    owner._main_deferred_eligible = lambda stmts: False
    owner._is_closed = lambda expr: False
    original_bind = owner._bind_names

    def joint_only_binding(joint, names, expr, **kw):
        result = original_bind(joint, names, expr, **kw)
        # Earlier value evaluation may already capture the classical name.
        # Restore the caller's joint-only precondition, without substituting
        # the caller or the capture hook. Original source regressions remain
        # read-only in the adjacent suite.
        for bound in names:
            if bound in ('duration', 'J', 'h'):
                owner.scalars.pop(bound, None)
        return result

    owner._bind_names = joint_only_binding
    result = execute_legacy_ast_body(owner, compiled.unit, stdout=io.StringIO())
    assert result.measure is not None
    assert isinstance(owner.scalars[name], float)
    assert owner.scalars[name] == (0.7 if name == 'duration' else 1.0545718e-19)
    assert any(path.endswith('/evaluation/execution.py') and called == name
               for path, called in owner.capture_calls)


@pytest.mark.parametrize('kind', ['instance', 'subclass'])
def test_s06_real_observation_method_duration_hook_and_value(kind):
    compiled = compile_source(_EVOLVE_FOR_METHOD_FLOAT)
    assert compiled.unit is not None, compiled.diagnostics
    owner = recording_owner(kind)
    owner._main_interproc_trace_eligible = lambda stmts: False
    owner._main_deferred_eligible = lambda stmts: False
    execute_legacy_ast_body(owner, compiled.unit, stdout=io.StringIO())
    owner.capture_calls.clear()
    owner.scalars.pop('duration', None)
    # Force all declared coordinates into the actual mechanics, not an
    # alternate lowered plan; caller and hook are unchanged production code.
    owner._deferred_bind_cone = lambda pending, expr, **kw: {
        name for stmt in pending for name in stmt.names
    }
    result = _run_deferred_state_binds(
        owner, Joint.unit(), compiled.unit.main.body.stmts[1:],
        logs=[], inspect_out=None, stdout=io.StringIO(),
    )
    assert result[1] is not None
    # The scalar stores the unit-local value; unit metadata is separate.
    assert owner.scalars['duration'] == 0.7
    assert owner.scalar_units['duration'] == 'fs'
    assert any(path.endswith('/evaluation/observation.py') and name == 'duration'
               for path, name in owner.capture_calls)


@pytest.mark.parametrize('route', ['execution', 'observation'])
@pytest.mark.parametrize('known', [False, True])
def test_s06_actual_consumer_eligibility_existing_key_excluded_and_multibind(route, known, monkeypatch):
    source = '''package t
pub fn main() -> Unit {
    Float x = 2.0
    State q = |0>
    a, b = 3.0, 4.0
    Measure q
}
'''
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    owner = recording_owner('instance')
    if route == 'observation':
        _prepare_first_family_context(owner, compiled.unit)
        owner._deferred_bind_cone = lambda pending, expr, **kw: {
            name for stmt in pending for name in stmt.names
        }
    else:
        owner._main_interproc_trace_eligible = lambda stmts: False
        owner._main_deferred_eligible = lambda stmts: False
        # Prevent earlier closed-expression shortcut so this exact caller's
        # post-binding eligibility is independently exercised.
        owner._is_closed = lambda expr: False
        original_prepare = execution._prepare_execution_context

        def prepare(context, unit):
            result = original_prepare(context, unit)
            if known:
                owner.scalars['x'] = 99
            return result

        monkeypatch.setattr(execution, '_prepare_execution_context', prepare)
    if known and route == 'observation':
        owner.scalars['x'] = 99
    if route == 'execution':
        execute_legacy_ast_body(owner, compiled.unit, stdout=io.StringIO())
    else:
        _run_deferred_state_binds(
            owner, Joint.unit(), compiled.unit.main.body.stmts,
            logs=[], inspect_out=None, stdout=io.StringIO(),
        )
    calls = [name for path, name in owner.capture_calls
             if path.endswith('/evaluation/' + route + '.py')]
    assert calls == ([] if known and route == 'execution' else ['x'])
    assert owner.scalars['x'] == (99 if known else 2.0)
    assert 'q' not in owner.scalars
    if route == 'observation':
        assert 'a' not in owner.scalars and 'b' not in owner.scalars


def caller_condition(module):
    tree = ast.parse(Path(module.__file__).read_text())
    guards = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        for statement in node.body:
            if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
                continue
            function = statement.value.func
            if isinstance(function, ast.Attribute) and function.attr == '_maybe_capture_classical_scalar':
                guards.append(node)
    assert len(guards) == 1
    return compile(ast.Expression(guards[0].test), '<actual capture caller>', 'eval')


@pytest.mark.parametrize('route', ['execution', 'observation'])
@pytest.mark.parametrize('ty,expected', [
    ('State', False), ('Operator', False), ('Delta', False), ('POVM', False),
    ('DensityState', False), ('QubitRegister', False), ('Float', True), (None, False),
])
def test_s06_each_excluded_type_uses_actual_caller_condition(route, ty, expected):
    module = execution if route == 'execution' else sys.modules[_run_deferred_state_binds.__module__]
    stmt = types.SimpleNamespace(ty=None if ty is None else types.SimpleNamespace(name=ty), names=['x'])
    context = types.SimpleNamespace(scalars={}, classes={}, structs={}, enums={})
    condition = caller_condition(module)
    assert eval(condition, {}, {'stmt': stmt, 'context': context}) is expected
    stmt.names = ['x', 'y']
    assert eval(condition, {}, {'stmt': stmt, 'context': context}) is False


@pytest.mark.parametrize('registry', ['classes', 'structs', 'enums'])
def test_s06_execution_registered_object_types_are_excluded(registry):
    context = types.SimpleNamespace(scalars={}, classes={}, structs={}, enums={})
    getattr(context, registry)['ObjectType'] = object()
    stmt = types.SimpleNamespace(ty=types.SimpleNamespace(name='ObjectType'), names=['x'])
    condition = caller_condition(execution)
    assert eval(condition, {}, {'stmt': stmt, 'context': context}) is False

