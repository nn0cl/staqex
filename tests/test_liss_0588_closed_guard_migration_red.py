"""C09 real preservation guard and copies across distinct AST-only shapes."""

import ast

import pytest

from tests import liss_0588_guard_support as closed
from tests import test_liss_0583_repair_boundary_migration_red as foreach
from tests import test_liss_0584_repair_boundary_red as repair
from tests import test_liss_0585_tensor_guard_migration_red as tensor
from tests import test_liss_0586_host_guard_migration_red as host
from tests import test_liss_0587_partial_guard_migration_red as partial
from tests import liss_0587_guard_support as partial_support


@pytest.fixture
def guarded(tmp_path):
    tensor.copy_guarded_dependencies(closed.ROOT, tmp_path)
    path = 'compiler/staqex/runtime/evaluation/static_foreach.py'
    (tmp_path / path).write_bytes((closed.ROOT / path).read_bytes())
    return tmp_path


def check(directory, monkeypatch):
    monkeypatch.setattr(repair, 'ROOT', directory)
    repair.test_existing_f05_owner_and_readonly_dependencies_are_preserved()


@pytest.mark.parametrize('extracted', [False, True], ids=['pre-closed', 'post-closed'])
def test_c09_real_guard_and_four_actual_copy_fixtures(guarded, monkeypatch, extracted):
    closed.make_shape(guarded, extracted)
    closed.assert_shape(guarded, extracted)
    check(guarded, monkeypatch)
    for suite in [foreach, tensor, host, partial]:
        with monkeypatch.context() as m:
            m.setattr(suite, 'ROOT', guarded, raising=False)
            m.setattr(partial_support, 'ROOT', guarded)
            m.setattr(tensor, 'ROOT', guarded)
            destination = guarded / suite.__name__.split('.')[-1]
            if suite is host:
                copied = suite.guarded.__wrapped__(destination)
            elif suite is partial:
                copied = suite.guarded.__wrapped__(destination)
            else:
                copied = suite.guarded_tree.__wrapped__(destination, m)
            closed.assert_shape(copied, extracted)
            check(copied, m)
            if extracted:
                path = copied / closed.SUCCESSOR
                original = path.read_text()
                path.write_text(original.replace('return False', 'return True', 1))
                with pytest.raises(AssertionError):
                    check(copied, m)
                path.write_text(original)
                path.unlink()  # This exact copied file in pytest's root only.
                with pytest.raises(AssertionError, match='missing closed successor'):
                    check(copied, m)


@pytest.mark.parametrize('path,old,new', [
    (closed.SUCCESSOR, 'return expr.name in context.scalars', 'return expr.name in context.objects'),
    (closed.SUCCESSOR, 'context._is_closed(expr.lhs) and context._is_closed(expr.rhs)', 'context._is_closed(expr.rhs) and context._is_closed(expr.lhs)'),
    (closed.SUCCESSOR, 'context._is_closed(expr.lhs) and context._is_closed(expr.rhs)', 'context._is_closed(expr.lhs) or context._is_closed(expr.rhs)'),
    (closed.SUCCESSOR, 'return context._is_closed(expr.expr)', 'return is_closed(context, expr.expr)'),
    (closed.SUCCESSOR, 'from ...dimensions import UNIT_TABLE', 'from ..dimensions import UNIT_TABLE'),
    (closed.SUCCESSOR, 'from typing import Any, Mapping, Protocol', 'from typing import Any, Mapping, Protocol\nfrom ...dimensions import UNIT_TABLE'),
    (closed.SUCCESSOR, 'from typing import Any, Mapping, Protocol', 'from typing import Any, Mapping, Protocol\nfrom ..evaluator import Evaluator'),
    (closed.SUCCESSOR, 'scalars: Mapping[str, Any]', 'scalars: Mapping[str, Any] = {}'),
    (closed.SUCCESSOR, 'return False', 'return True'),
    (closed.EVALUATOR, closed.HOOK, '_is_closed = staticmethod(_is_closed_successor)'),
    (closed.EVALUATOR, closed.HOOK, '_is_closed = _fill_partial_successor'),
    (closed.EVALUATOR, closed.IMPORT, closed.IMPORT + '\n' + closed.IMPORT),
    (closed.EVALUATOR, 'return self.static_register_sizes.get(name)', 'return 99'),
])
def test_c09_real_guard_rejects_algorithm_protocol_dependency_and_hook_mutations(guarded, monkeypatch, path, old, new):
    closed.make_shape(guarded, True)
    check(guarded, monkeypatch)
    target = guarded / path
    source = target.read_text()
    assert old in source, 'mutation must actually change protected source'
    target.write_text(source.replace(old, new, 1))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


@pytest.mark.parametrize('mutation', ['missing-successor', 'missing-hook', 'duplicate-hook', 'duplicate-body', 'extra-state'])
def test_c09_missing_duplicate_and_extra_state_rejected(guarded, monkeypatch, mutation):
    closed.make_shape(guarded, True)
    check(guarded, monkeypatch)
    path = guarded / closed.EVALUATOR
    tree = ast.parse(path.read_text())
    cls = closed.owner(tree)
    if mutation == 'missing-successor':
        (guarded / closed.SUCCESSOR).unlink()
    elif mutation == 'missing-hook':
        cls.body = [n for n in cls.body if closed.dump(n) != closed.dump(ast.parse(closed.HOOK).body[0])]
    elif mutation == 'duplicate-hook':
        cls.body.append(ast.parse(closed.HOOK).body[0])
    elif mutation == 'duplicate-body':
        cls.body.append(closed.original_method())
    else:
        cls.body.append(ast.parse('extra_state = {}').body[0])
    path.write_text(ast.unparse(ast.fix_missing_locations(tree)))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


@pytest.mark.parametrize('extracted', [False, True])
def test_c09_retained_old_body_and_original_foreach_mutation_setup(guarded, monkeypatch, extracted):
    closed.make_shape(guarded, extracted)
    closed.assert_shape(guarded, extracted)
    check(guarded, monkeypatch)
    # Invoke an unchanged real inherited old-body mutation test on this root.
    foreach.test_real_guard_rejects_changed_retained_old_body(guarded)
    closed.make_shape(guarded, False)
    # Foreach mutation remains intentionally rejected; use a fresh copy for closed.
    fresh = guarded / 'fresh-closed'
    tensor.copy_guarded_dependencies(closed.ROOT, fresh)
    closed.make_shape(fresh, False)
    check(fresh, monkeypatch)
    target = fresh / closed.EVALUATOR
    source = target.read_text()
    target.write_text(source.replace('return expr.name in self.scalars', 'return True', 1))
    with pytest.raises(AssertionError):
        check(fresh, monkeypatch)


def test_c09_original_fixture_is_immutable(tmp_path, monkeypatch):
    assert closed.original_method().name == '_is_closed'
    target = tmp_path / 'changed.txt'
    target.write_bytes(closed.FIXTURE.read_bytes() + b'\n')
    monkeypatch.setattr(closed, 'FIXTURE', target)
    with pytest.raises(AssertionError, match='evidence changed'):
        closed.original_method()


@pytest.mark.parametrize('path', foreach.BYTE_PATHS)
def test_c09_persistent_byte_guards_still_reject_changes(guarded, monkeypatch, path):
    closed.make_shape(guarded, True)
    check(guarded, monkeypatch)
    target = guarded / path
    target.write_bytes(target.read_bytes() + b'\n# unapproved\n')
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)
