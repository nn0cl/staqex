"""S01–S05 live-owner characterization through the retained real private hook."""

import copy
from fractions import Fraction
import math

import pytest

from compiler.staqex.runtime.evaluator import Evaluator
from compiler.staqex.runtime.joint import Joint, World


class MarginalStub:
    def __init__(self, values=None, error=None, callback=None):
        self.values = values
        self.error = error
        self.callback = callback
        self.calls = []

    def marginal(self, name):
        self.calls.append(name)
        if self.callback is not None:
            self.callback()
        if self.error is not None:
            raise self.error
        return self.values


def owner(scalars=None):
    instance = Evaluator.__new__(Evaluator)
    instance.scalars = {} if scalars is None else scalars
    return instance


def capture(instance, joint, name='x'):
    return instance._maybe_capture_classical_scalar(joint, name)


@pytest.mark.parametrize('stored', [0, False, None, Fraction(1, 3)])
def test_s01_existing_key_short_circuits_without_reading_joint(stored):
    instance = owner({'x': stored})
    joint = MarginalStub(error=AssertionError('must not acquire marginal'))
    assert capture(instance, joint) is None
    assert instance.scalars['x'] is stored
    assert joint.calls == []


def test_s01_membership_error_is_not_swallowed():
    class BrokenMembership(dict):
        def __contains__(self, key):
            raise ValueError('membership')

    joint = MarginalStub({1: 1})
    with pytest.raises(ValueError, match='membership'):
        capture(owner(BrokenMembership()), joint)
    assert joint.calls == []


@pytest.mark.parametrize('error', [ValueError, TypeError, RuntimeError, KeyError, OverflowError])
def test_s02_marginal_exception_is_swallowed_with_exact_call(error):
    instance = owner()
    joint = MarginalStub(error=error('acquisition'))
    assert capture(instance, joint, 'duration') is None
    assert joint.calls == ['duration']
    assert instance.scalars == {}


def test_s02_base_exception_propagates():
    class Interrupt(BaseException):
        pass

    with pytest.raises(Interrupt):
        capture(owner(), MarginalStub(error=Interrupt()))


@pytest.mark.parametrize('joint', [
    Joint.empty(), Joint.unit(), Joint([World({'x': 1}, 0j)]),
    Joint([World({'x': 1}, 0.5), World({'x': 2}, 0.5)]),
])
def test_s02_real_empty_missing_vacuum_and_multivalue_do_not_capture(joint):
    instance = owner({'keep': 9})
    before = copy.deepcopy(joint)
    assert capture(instance, joint) is None
    assert instance.scalars == {'keep': 9}
    assert joint == before


@pytest.mark.parametrize('stage', ['len', 'iter', 'next'])
def test_s02_cardinality_and_key_iteration_errors_propagate(stage):
    class BrokenMarginal:
        def __len__(self):
            if stage == 'len':
                raise ValueError('outside catch')
            return 1

        def __iter__(self):
            if stage == 'iter':
                raise ValueError('outside catch')
            return self

        def __next__(self):
            raise ValueError('outside catch')

    with pytest.raises(ValueError, match='outside catch'):
        capture(owner(), MarginalStub(BrokenMarginal()))


def test_s02_non_singleton_never_converts_a_key():
    class RaisingKey:
        def __float__(self):
            raise AssertionError('conversion must not happen')

    instance = owner()
    assert capture(instance, MarginalStub({RaisingKey(): 0.5, RaisingKey(): 0.5})) is None
    assert instance.scalars == {}


@pytest.mark.parametrize('raw,expected', [
    (2, 2.0), (2.5, 2.5), (True, 1.0), (False, 0.0), ('3.25', 3.25), (-0.0, -0.0),
])
def test_s03_non_fraction_key_float_conversion_ignores_mass(raw, expected):
    instance = owner()
    joint = MarginalStub({raw: 0.0})
    assert capture(instance, joint) is None
    assert type(instance.scalars['x']) is float
    assert instance.scalars['x'] == expected
    if expected == 0:
        assert math.copysign(1, instance.scalars['x']) == math.copysign(1, expected)
    assert joint.calls == ['x']


@pytest.mark.parametrize('subclass', [False, True])
def test_s03_fraction_key_retains_exact_identity(subclass):
    class ExactFraction(Fraction):
        def __float__(self):
            raise AssertionError('Fraction must not convert')

    raw = (ExactFraction if subclass else Fraction)(1, 3)
    instance = owner()
    assert capture(instance, MarginalStub({raw: 0.25})) is None
    assert instance.scalars['x'] is raw


@pytest.mark.parametrize('repeated', [False, True])
def test_s03_real_deterministic_joint_and_equal_values_preserve_worlds(repeated):
    joint = Joint([World({'x': 7}, 0.5), World({'x': 7}, 0.5)] if repeated else [World({'x': 7}, 1)])
    before = copy.deepcopy(joint)
    instance = owner({'keep': 9})
    assert capture(instance, joint) is None
    assert instance.scalars == {'keep': 9, 'x': 7.0}
    assert joint == before


@pytest.mark.parametrize('raw', [None, object(), 'not-numeric'])
def test_s04_invalid_conversion_is_swallowed_without_ordinary_map_write(raw):
    instance = owner()
    assert capture(instance, MarginalStub({raw: 1})) is None
    assert instance.scalars == {}


@pytest.mark.parametrize('error', [TypeError, ValueError, OverflowError, RuntimeError])
def test_s04_custom_conversion_exact_exception_boundary(error):
    class Conversion:
        def __float__(self):
            raise error('conversion')

    instance = owner()
    joint = MarginalStub({Conversion(): 1})
    if error in (TypeError, ValueError):
        assert capture(instance, joint) is None
    else:
        with pytest.raises(error, match='conversion'):
            capture(instance, joint)
    assert instance.scalars == {}


@pytest.mark.parametrize('error', [TypeError, ValueError, OverflowError, RuntimeError])
@pytest.mark.parametrize('raw', [2, Fraction(1, 3)])
def test_s04_assignment_exact_exception_boundary_in_both_paths(error, raw):
    class BrokenWrite(dict):
        def __setitem__(self, key, value):
            raise error('assignment')

    instance = owner(BrokenWrite())
    if error in (TypeError, ValueError):
        assert capture(instance, MarginalStub({raw: 1})) is None
    else:
        with pytest.raises(error, match='assignment'):
            capture(instance, MarginalStub({raw: 1}))
    assert instance.scalars == {}


@pytest.mark.parametrize('raw', [float('nan'), float('inf'), -float('inf')])
def test_s04_nonfinite_conversion_remains_unchanged(raw):
    instance = owner()
    assert capture(instance, MarginalStub({raw: 1})) is None
    result = instance.scalars['x']
    assert math.isnan(result) if math.isnan(raw) else result == raw


def test_s04_mutating_map_is_not_rolled_back_after_swallowed_error():
    class MutatingWrite(dict):
        def __setitem__(self, key, value):
            super().__setitem__(key, value)
            raise ValueError('after write')

    instance = owner(MutatingWrite())
    assert capture(instance, MarginalStub({2: 1})) is None
    assert instance.scalars == {'x': 2.0}


def test_s05_repeated_calls_map_replacement_and_separate_owners():
    first, second = owner(), owner()
    capture(first, MarginalStub({2: 1}))
    skipped = MarginalStub(error=AssertionError('already captured'))
    capture(first, skipped)
    assert skipped.calls == []
    first.scalars = {'other': 8}
    capture(first, MarginalStub({3: 1}))
    capture(second, MarginalStub({4: 1}))
    assert first.scalars == {'other': 8, 'x': 3.0}
    assert second.scalars == {'x': 4.0}


def test_s05_marginal_replacement_uses_current_map_not_snapshot():
    instance = owner({'keep': 8})
    original = instance.scalars
    replacement = {'new': 9}
    joint = MarginalStub({2: 1}, callback=lambda: setattr(instance, 'scalars', replacement))
    capture(instance, joint)
    assert original == {'keep': 8}
    assert instance.scalars is replacement
    assert replacement == {'new': 9, 'x': 2.0}


def test_s05_marginal_insertion_does_not_add_a_second_membership_check():
    instance = owner()
    joint = MarginalStub({2: 1}, callback=lambda: instance.scalars.update(x=99))
    capture(instance, joint)
    assert instance.scalars == {'x': 2.0}
