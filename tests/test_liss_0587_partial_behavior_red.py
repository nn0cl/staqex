"""P01–P04/P06 behavior characterization through the retained real hook."""

import base64
from dataclasses import fields, is_dataclass
import hashlib
import pickle

import pytest

from compiler.staqex.ast_nodes import Call, LitInt, Span, Var
from compiler.staqex.runtime.evaluator import Evaluator, KernelError, PartialValue
from tests import liss_0587_guard_support as partial


def literal(value):
    return LitInt(value=value, span=Span(line=value + 1, col=3))


@pytest.mark.parametrize("slots", [(None, 7, None, 8), (None, 7, 8, None), (7, None, 8, None)])
def test_p01_left_to_right_preserves_inputs_and_occupied_identity(slots):
    original = [None if value is None else literal(value) for value in slots]
    value = PartialValue("f", original)
    argument = literal(2)
    args = [argument]
    result = Evaluator._fill_partial(value, args)
    assert isinstance(result, PartialValue)
    assert result is not value and result.slots is not original
    expected = list(original)
    expected[expected.index(None)] = argument
    assert len(result.slots) == len(expected)
    assert all(a is b for a, b in zip(result.slots, expected))
    assert value.slots is original and original == [None if v is None else literal(v) for v in slots]
    assert args == [argument] and args[0] is argument


def test_p02_repeated_stepwise_fill_keeps_original_values():
    fixed, first, second, third = (literal(n) for n in range(4))
    original = PartialValue("f", [None, fixed, None, None])
    one = Evaluator._fill_partial(original, [first])
    two = Evaluator._fill_partial(one, [second])
    result = Evaluator._fill_partial(two, [third])
    assert type(one) is type(two) is PartialValue
    assert one.fun_name == two.fun_name == "f"
    assert original.slots == [None, fixed, None, None]
    assert one.slots == [first, fixed, None, None]
    assert two.slots == [first, fixed, second, None]
    assert isinstance(result, Call)
    assert all(a is b for a, b in zip(result.args, [first, fixed, second, third]))


@pytest.mark.parametrize("slots", [(None, 7, None), (7, None, None)])
def test_p03_exact_fill_preserves_order_and_first_argument_span(slots):
    fixed = literal(7)
    original = [None if n is None else fixed for n in slots]
    first, second = literal(1), literal(2)
    args = [first, second]
    result = Evaluator._fill_partial(PartialValue("target", original), args)
    assert isinstance(result, Call) and isinstance(result.callee, Var)
    assert result.callee.name == "target"
    assert result.span is first.span and result.callee.span is first.span
    replacements = iter(args)
    expected = [next(replacements) if n is None else fixed for n in slots]
    assert len(result.args) == len(expected)
    assert all(a is b for a, b in zip(result.args, expected))
    assert result.args is not args and original == [None if n is None else fixed for n in slots]


@pytest.mark.parametrize("slots,count,need", [([None], 0, 1), ([None], 2, 1), ([], 0, 0), ([], 1, 0), ([7], 0, 0), ([7], 1, 0)])
def test_p04_invalid_arity_has_exact_error_and_no_mutation(slots, count, need):
    original = [None if n is None else literal(n) for n in slots]
    value = PartialValue("target", original)
    args = [literal(n) for n in range(count)]
    before, args_before = list(original), list(args)
    with pytest.raises(KernelError) as error:
        Evaluator._fill_partial(value, args)
    assert type(error.value) is KernelError
    assert str(error.value) == f"Partial `target` expects 1..{need} remaining args, got {count}"
    assert value.slots is original and original == before and args == args_before


def test_p06_legacy_and_current_pickle_dataclass_compatibility():
    fixture = partial.FIXTURE.parent / "legacy-partial-pickle.b64"
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == (
        "9caa3d599ad9402d3e7cbe1f9e24904a9e1e4fcf1201aa2199f6d75643a707a7"
    )
    encoded = fixture.read_text()
    legacy = pickle.loads(base64.b64decode(encoded))
    assert type(legacy) is PartialValue and legacy.fun_name == "legacy" and legacy.slots == [None]
    assert PartialValue.__name__ == "PartialValue" and PartialValue.__module__ == partial.MODULE
    assert is_dataclass(PartialValue)
    assert [f.name for f in fields(PartialValue)] == ["fun_name", "slots"]
    value = PartialValue("f", [None, literal(2)])
    assert repr(value).startswith("PartialValue(fun_name='f', slots=")
    restored = pickle.loads(pickle.dumps(value))
    assert type(restored) is PartialValue and restored == value
    restored.fun_name = "changed"
    restored.slots.append(None)
    assert restored != value and value.fun_name == "f" and len(value.slots) == 2


def test_p06_retained_hook_works_as_class_and_instance_static_call():
    value = PartialValue("f", [None, None])
    args = [literal(1)]
    instance = Evaluator.__new__(Evaluator)
    assert isinstance(Evaluator.__dict__["_fill_partial"], staticmethod)
    assert Evaluator._fill_partial(value, args) == instance._fill_partial(value, args)
    assert instance.__dict__ == {}  # No evaluator initialization/state needed.
