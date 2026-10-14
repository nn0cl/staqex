"""S09 real guard/copy setup on distinct, never-imported scalar AST shapes."""

import ast

import pytest

from tests import liss_0589_guard_support as capture
from tests import liss_0587_guard_support as partial_support
from tests import test_liss_0583_repair_boundary_migration_red as foreach
from tests import test_liss_0584_repair_boundary_red as repair
from tests import test_liss_0585_tensor_guard_migration_red as tensor
from tests import test_liss_0586_host_guard_migration_red as host
from tests import test_liss_0587_partial_guard_migration_red as partial
from tests import test_liss_0588_closed_guard_migration_red as closed_tests


@pytest.fixture
def guarded(tmp_path):
    tensor.copy_guarded_dependencies(capture.ROOT, tmp_path)
    path = 'compiler/staqex/runtime/evaluation/static_foreach.py'
    (tmp_path / path).write_bytes((capture.ROOT / path).read_bytes())
    return tmp_path


def check(directory, monkeypatch):
    monkeypatch.setattr(repair, 'ROOT', directory)
    repair.test_existing_f05_owner_and_readonly_dependencies_are_preserved()


@pytest.mark.parametrize('extracted', [False, True], ids=['pre-capture', 'post-capture'])
def test_s09_real_guard_and_four_actual_copied_fixtures(guarded, monkeypatch, extracted):
    capture.make_shape(guarded, extracted)
    capture.assert_shape(guarded, extracted)
    check(guarded, monkeypatch)
    for suite in [foreach, tensor, host, partial]:
        with monkeypatch.context() as m:
            m.setattr(suite, 'ROOT', guarded, raising=False)
            m.setattr(partial_support, 'ROOT', guarded)
            m.setattr(tensor, 'ROOT', guarded)
            destination = guarded / suite.__name__.split('.')[-1]
            if suite in (host, partial):
                copied = suite.guarded.__wrapped__(destination)
            else:
                copied = suite.guarded_tree.__wrapped__(destination, m)
            capture.assert_shape(copied, extracted)
            check(copied, m)
            if extracted:
                path = copied / capture.SUCCESSOR
                original = path.read_text()
                assert 'len(marg) != 1' in original
                path.write_text(original.replace('len(marg) != 1', 'len(marg) == 1', 1))
                with pytest.raises(AssertionError):
                    check(copied, m)
                path.write_text(original)
                path.unlink()  # Exact copied file under pytest temporary root only.
                with pytest.raises(AssertionError, match='missing scalar capture successor'):
                    check(copied, m)


@pytest.mark.parametrize('path,old,new', [
    (capture.SUCCESSOR, 'if name in context.scalars:', 'if name not in context.scalars:'),
    (capture.SUCCESSOR, 'len(marg) != 1', 'len(marg) == 1'),
    (capture.SUCCESSOR, 'joint.marginal(name)', 'joint.marginal("other")'),
    (capture.SUCCESSOR, 'except Exception:', 'except BaseException:'),
    (capture.SUCCESSOR, 'except (TypeError, ValueError):', 'except Exception:'),
    (capture.SUCCESSOR, 'raw = next(iter(marg))', 'raw = next(iter(marg.values()))'),
    (capture.SUCCESSOR, 'isinstance(raw, Fraction)', 'isinstance(raw, float)'),
    (capture.SUCCESSOR, 'context.scalars[name] = raw', 'context.scalars[name] = float(raw)'),
    (capture.SUCCESSOR, 'context.scalars[name] = float(raw)', 'context.scalars[name] = raw'),
    (capture.SUCCESSOR, 'raw = next(iter(marg))', 'context.scalars = dict(context.scalars)\n    raw = next(iter(marg))'),
    (capture.SUCCESSOR, 'name: str', 'name: int'),
    (capture.SUCCESSOR, 'from ..joint import Joint', 'from ..joint import Joint\nextra_state = {}'),
    (capture.SUCCESSOR, 'from ..joint import Joint', 'from .joint import Joint'),
    (capture.SUCCESSOR, 'from ..joint import Joint', 'from ..joint import Joint\nfrom ..evaluator import Evaluator'),
    (capture.SUCCESSOR, 'scalars: MutableMapping[str, float | Fraction]', 'scalars: MutableMapping[str, float | Fraction] = {}'),
    (capture.EVALUATOR, capture.HOOK, '_maybe_capture_classical_scalar = staticmethod(_capture_classical_scalar_successor)'),
    (capture.EVALUATOR, capture.HOOK, '_maybe_capture_classical_scalar = _is_closed_successor'),
    (capture.EVALUATOR, capture.IMPORT, capture.IMPORT + '\n' + capture.IMPORT),
    (capture.EVALUATOR, 'return self.static_register_sizes.get(name)', 'return 99'),
])
def test_s09_real_guard_rejects_algorithm_exception_protocol_dependency_hook_mutations(guarded, monkeypatch, path, old, new):
    capture.make_shape(guarded, True)
    check(guarded, monkeypatch)
    target = guarded / path
    source = target.read_text()
    assert old in source, 'mutation must actually change protected source'
    target.write_text(source.replace(old, new, 1))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


@pytest.mark.parametrize('mutation', ['missing-successor', 'missing-hook', 'duplicate-hook', 'duplicate-body', 'extra-state'])
def test_s09_missing_duplicate_and_extra_state_rejected(guarded, monkeypatch, mutation):
    capture.make_shape(guarded, True)
    check(guarded, monkeypatch)
    tree = ast.parse((guarded / capture.EVALUATOR).read_text())
    cls = capture.owner(tree)
    if mutation == 'missing-successor':
        (guarded / capture.SUCCESSOR).unlink()
    elif mutation == 'missing-hook':
        cls.body = [n for n in cls.body if capture.dump(n) != capture.dump(ast.parse(capture.HOOK).body[0])]
    elif mutation == 'duplicate-hook':
        cls.body.append(ast.parse(capture.HOOK).body[0])
    elif mutation == 'duplicate-body':
        cls.body.append(capture.original_method())
    else:
        cls.body.append(ast.parse('extra_state = {}').body[0])
    (guarded / capture.EVALUATOR).write_text(ast.unparse(ast.fix_missing_locations(tree)))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


@pytest.mark.parametrize('extracted', [False, True])
def test_s09_original_body_and_inherited_mutation_setup_are_effective(guarded, monkeypatch, extracted):
    capture.make_shape(guarded, extracted)
    capture.assert_shape(guarded, extracted)
    check(guarded, monkeypatch)
    # Invoke unchanged real inherited tests on the future scalar shape.
    closed_tests.test_c09_retained_old_body_and_original_foreach_mutation_setup(
        guarded, monkeypatch, True,
    )
    fresh = guarded / 'fresh-scalar'
    tensor.copy_guarded_dependencies(capture.ROOT, fresh)
    capture.make_shape(fresh, False)
    check(fresh, monkeypatch)
    path = fresh / capture.EVALUATOR
    source = path.read_text()
    assert 'len(marg) != 1' in source
    path.write_text(source.replace('len(marg) != 1', 'len(marg) == 1', 1))
    with pytest.raises(AssertionError):
        check(fresh, monkeypatch)


def test_s09_original_fixture_is_immutable(tmp_path, monkeypatch):
    assert capture.original_method().name == '_maybe_capture_classical_scalar'
    target = tmp_path / 'changed.txt'
    target.write_bytes(capture.FIXTURE.read_bytes() + b'\n')
    monkeypatch.setattr(capture, 'FIXTURE', target)
    with pytest.raises(AssertionError, match='evidence changed'):
        capture.original_method()


@pytest.mark.parametrize('path', foreach.BYTE_PATHS)
def test_s09_persistent_byte_guards_still_reject_changes(guarded, monkeypatch, path):
    capture.make_shape(guarded, True)
    check(guarded, monkeypatch)
    target = guarded / path
    target.write_bytes(target.read_bytes() + b'\n# unapproved change\n')
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)
