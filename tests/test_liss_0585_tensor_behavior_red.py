"""T01–T06: existing private hook behavior, independent of ownership Red."""

import copy
from types import SimpleNamespace

import pytest

from compiler.staqex.ast_nodes import Call, KetLit, TensorExpr, Var
from compiler.staqex.runtime.evaluator import Evaluator, KernelError
from compiler.staqex.runtime.evaluation.binding import bind_names, bind
from compiler.staqex.runtime.joint import Joint, World


def var(name):
    return Var(name=name, span=None)


def tensor(left=None, right=None):
    return TensorExpr(left=left or var("l"), right=right or var("r"), span=None)


def snapshot(joint):
    return [(w.assign, w.amp, w.coord_phase) for w in joint.worlds]


def record_sides(left, right):
    events = []

    def bind(joint, name, expr):
        events.append((joint, name, expr))
        result = (left, right)[len(events) - 1]
        if isinstance(result, Exception):
            raise result
        return result

    return SimpleNamespace(_bind=bind), events


def independent(left, right, expr=None, names=None):
    context, events = record_sides(left, right)
    result = Evaluator._bind_tensor(
        context, Joint([World({"unrelated": 99}, 7j)]), names or ["a", "b"],
        expr or tensor(KetLit("0", None), KetLit("1", None)),
    )
    return result, events


@pytest.mark.parametrize("names", [[], ["a"], ["a", "b", "c"]])
def test_t01_output_arity_rejects_before_callbacks(names):
    context, events = record_sides(Joint.unit(), Joint.unit())
    with pytest.raises(KernelError) as caught:
        Evaluator._bind_tensor(context, Joint.unit(), names, tensor())
    assert str(caught.value) == "`*|*` / tensor bind expects two names `(a, b) = …`"
    assert events == []


@pytest.mark.parametrize("arity", [0, 1, 3])
def test_t01_alias_arity_and_single_name_diagnostics(arity):
    context, events = record_sides(Joint.unit(), Joint.unit())
    call = Call(var("tensor"), [var("l")] * arity, None)
    with pytest.raises(KernelError) as caught:
        bind_names(context, Joint.unit(), ["a", "b"], call)
    assert str(caught.value) == "tensor requires exactly two arguments"
    with pytest.raises(KernelError) as caught:
        bind(context, Joint.unit(), "a", tensor())
    assert str(caught.value) == "tensor product requires tuple bind `(a, b) = left *|* right`"
    assert events == []


def test_t02_relabel_preserves_correlations_complex_amp_and_phases_without_mutation():
    joint = Joint([
        World({"l": 0, "r": 0, "other": 8}, 1 + 2j, {"l": 1j, "r": -1j, "other": -1}),
        World({"l": 1, "r": 1, "other": 9}, -2j, {"l": -1, "other": 1j}),
    ])
    before = copy.deepcopy(joint)
    context, events = record_sides(None, None)
    result = Evaluator._bind_tensor(context, joint, ["a", "b"], tensor())
    assert snapshot(result) == [
        ({"a": 0, "b": 0, "other": 8}, 1 + 2j, {"a": 1j, "b": -1j, "other": -1}),
        ({"a": 1, "b": 1, "other": 9}, -2j, {"a": -1, "other": 1j}),
    ]
    assert joint == before and events == []


@pytest.mark.parametrize("assignment", [{"l": 0}, {"r": 0}, {}])
def test_t03_missing_coordinates_at_later_world_leave_input_unchanged(assignment):
    joint = Joint([World({"l": 1, "r": 2}, 1j), World(assignment, 2)])
    before = copy.deepcopy(joint)
    context, events = record_sides(None, None)
    with pytest.raises(KernelError) as caught:
        Evaluator._bind_tensor(context, joint, ["a", "b"], tensor())
    assert str(caught.value) == "`*|*` needs coordinates `l` and `r` on the joint"
    assert joint == before and events == []


def test_t03_empty_var_joint_does_not_bind_independent_sides():
    context, events = record_sides(None, None)
    assert Evaluator._bind_tensor(context, Joint.empty(), ["a", "b"], tensor()) == Joint.empty()
    assert events == []


@pytest.mark.parametrize("mixed", [False, True])
def test_t04_live_callback_receives_fresh_units_original_expr_and_left_right_order(mixed):
    expr = tensor(var("l") if mixed else KetLit("0", None), KetLit("1", None))
    result, events = independent(Joint([World({"_T": 2}, 1)]), Joint([World({"_T": 3}, 1)]), expr)
    assert len(events) == 2
    assert events[0][0] == events[1][0] == Joint.unit()
    assert events[0][0] is not events[1][0]
    assert events[0][1] == events[1][1] == "_T"
    assert events[0][2] is expr.left and events[1][2] is expr.right
    assert snapshot(result) == [({"a": 2, "b": 3}, 1, {})]


@pytest.mark.parametrize("side", [0, 1])
def test_t04_callback_error_propagates_at_original_sequence_point(side):
    error = KernelError("original side failure")
    results = [Joint([World({"_T": 0}, 1)]), Joint([World({"_T": 1}, 1)])]
    results[side] = error
    context, events = record_sides(*results)
    with pytest.raises(KernelError) as caught:
        Evaluator._bind_tensor(context, Joint.unit(), ["a", "b"], tensor(KetLit("0", None), KetLit("1", None)))
    assert caught.value is error and len(events) == side + 1


def test_t05_product_order_amp_and_existing_independent_phase_handling():
    left = Joint([World({"_T": 0, "discard": 5}, 1j, {"_T": -1}), World({"_T": 1}, 2)])
    right = Joint([World({"_T": 2}, -1j, {"_T": 1j}), World({"_T": 3}, 3)])
    result, _ = independent(left, right)
    assert snapshot(result) == [
        ({"a": 0, "b": 2}, 1, {}), ({"a": 0, "b": 3}, 3j, {}),
        ({"a": 1, "b": 2}, -2j, {}), ({"a": 1, "b": 3}, 6, {}),
    ]


@pytest.mark.parametrize("amps,expected", [([1, 2j], 1 + 2j), ([1, -1], None)])
def test_t05_duplicate_assignments_coalesce_and_cancel(amps, expected):
    left = Joint([World({"_T": 0}, a) for a in amps])
    result, _ = independent(left, Joint([World({"_T": 1}, 1)]))
    assert snapshot(result) == ([] if expected is None else [({"a": 0, "b": 1}, expected, {})])


@pytest.mark.parametrize("empty_left,empty_right", [(True, False), (False, True), (True, True)])
def test_t05_both_callbacks_run_before_empty_support_check(empty_left, empty_right):
    side = Joint([World({"_T": 0}, 1)])
    result, events = independent(Joint.empty() if empty_left else side, Joint.empty() if empty_right else side)
    assert result == Joint.empty() and len(events) == 2


@pytest.mark.parametrize("names,left,right,expected,phases", [
    (["a", "b"], "l", "r", {"a": 1, "b": 2}, {"a": 1j, "b": -1j}),
    (["a", "a"], "l", "r", {"a": 2}, {"a": -1j}),
    (["a", "b"], "l", "l", {"r": 2, "a": 1, "b": 1}, {"r": -1j, "a": 1j, "b": 1j}),
    (["r", "l"], "l", "r", {"r": 1, "l": 2}, {"r": 1j, "l": -1j}),
    (["l", "r"], "l", "r", {"l": 1, "r": 2}, {"l": 1j, "r": -1j}),
])
def test_t06_relabel_name_collisions_follow_existing_assignment_order(names, left, right, expected, phases):
    joint = Joint([World({"l": 1, "r": 2, "a": 99, "b": 98}, 2j,
                         {"l": 1j, "r": -1j, "a": 7, "b": 8})])
    # Existing output coordinates not targeted by this case remain unrelated.
    expected = {**{k: v for k, v in joint.worlds[0].assign.items() if k not in {left, right}}, **expected}
    phases = {**{k: v for k, v in joint.worlds[0].coord_phase.items() if k not in {left, right}}, **phases}
    context, events = record_sides(None, None)
    result = Evaluator._bind_tensor(context, joint, names, tensor(var(left), var(right)))
    assert snapshot(result) == [(expected, 2j, phases)] and events == []


def test_t06_independent_identical_output_names_keep_right_assignment():
    result, _ = independent(Joint([World({"_T": 2}, 1j)]), Joint([World({"_T": 3}, 2)]), names=["a", "a"])
    assert snapshot(result) == [({"a": 3}, 2j, {})]


@pytest.mark.parametrize("alias", [False, True])
def test_t07_actual_bind_names_preserves_overridable_private_hook(alias):
    calls = []
    expression = tensor()
    value = Joint([World({"result": 1}, 1)])

    def hook(joint, names, expr):
        calls.append((joint, names, expr))
        return value

    context = SimpleNamespace(_bind_tensor=hook)
    incoming = Joint.unit()
    call = Call(var("tensor"), [expression.left, expression.right], "call-span")
    assert bind_names(context, incoming, ["a", "b"], call if alias else expression) is value
    assert calls[0][:2] == (incoming, ["a", "b"])
    assert calls[0][2].left is expression.left and calls[0][2].right is expression.right
    assert calls[0][2].span == ("call-span" if alias else expression.span)
