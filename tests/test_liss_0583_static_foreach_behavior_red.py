"""F01–F05 characterization through the real historical/successor hook."""

import importlib
from types import SimpleNamespace

import pytest

from compiler.staqex.ast_nodes import (
    Block, Call, ExprStmt, ForEachStmt, LitInt, Measure, Snapshot, Span, Var,
)
from compiler.staqex.runtime.evaluator import Evaluator, KernelError

SPAN = Span(7, 3)
CALL_SPAN = Span(8, 5)


def apply(operator="H", target=None, *, callee=None):
    return ExprStmt(Call(
        callee=callee if callee is not None else Var("apply", CALL_SPAN),
        args=[Var(operator, CALL_SPAN), target if target is not None else Var("q", SPAN)],
        span=CALL_SPAN,
    ), CALL_SPAN)


def loop(collection=None, body=None):
    return ForEachStmt("q", collection if collection is not None else Var("reg", SPAN),
                       Block(body if body is not None else [apply()], SPAN), SPAN)


@pytest.fixture
def recording(monkeypatch):
    events = []
    sizes = {"reg": 2}

    def bind_names(joint, names, expr, *, logs, inspect_out):
        events.append(("bind", joint, names, expr, logs, inspect_out))
        return joint + 1

    def bind_call(context, joint, name, expr):
        events.append(("apply", joint, name, expr, context))
        return joint + 10

    context = SimpleNamespace(static_register_sizes=sizes, _bind_names=bind_names)
    hook = Evaluator._run_foreach
    monkeypatch.setattr(importlib.import_module(hook.__module__), "bind_call", bind_call)
    return context, events, hook


@pytest.mark.parametrize("count", [1, 3])
def test_member_then_body_order_and_original_spans(recording, count):
    context, events, hook = recording
    context.static_register_sizes["reg"] = count
    first, second = apply("H"), apply("X")
    assert hook(context, 0, loop(body=[first, second])) == count * 21
    assert len(events) == count * 3
    for index in range(count):
        binding, h, x = events[index * 3:index * 3 + 3]
        wire = f"__foreach_q_{index}"
        assert binding[:3] == ("bind", index * 21, [wire])
        assert binding[3].label == "0" and binding[3].span is SPAN
        assert binding[4:] == ([], None)
        for event, original, incoming in ((h, first, index * 21 + 1), (x, second, index * 21 + 11)):
            assert event[:3] == ("apply", incoming, wire)
            call = event[3]
            assert call.callee is original.expr.callee
            assert call.args[0] is original.expr.args[0]
            assert call.args[1].name == wire and call.args[1].span is SPAN
            assert call.span is CALL_SPAN and event[4] is context
        assert first.expr.args[1].name == second.expr.args[1].name == "q"


def test_empty_body_binds_each_wire_and_threads_joint(recording):
    context, events, hook = recording
    assert hook(context, 9, loop(body=[])) == 11
    assert [e[0] for e in events] == ["bind", "bind"]


def register(*args):
    return Call(Var("register", SPAN), list(args), SPAN)


@pytest.mark.parametrize("collection,sizes", [
    (Var("missing", SPAN), {}),
    (Var("reg", SPAN), {"reg": 0}),
    (Var("reg", SPAN), {"reg": -1}),
    (LitInt(2, SPAN), {}),
    (register(), {}),
    (register(LitInt(0, SPAN)), {}),
    (register(LitInt(-1, SPAN)), {}),
    (register(Var("dynamic", SPAN)), {}),
    (register(LitInt(1, SPAN), LitInt(2, SPAN)), {}),
    (Call(LitInt(1, SPAN), [LitInt(2, SPAN)], SPAN), {}),
], ids=["missing", "zero-map", "negative-map", "non-register", "arity-zero",
        "zero-literal", "negative-literal", "dynamic", "arity-two", "nonvar-callee"])
def test_invalid_bounds_reject_before_callbacks(recording, collection, sizes):
    context, events, hook = recording
    context.static_register_sizes = sizes
    with pytest.raises(KernelError) as caught:
        hook(context, 99, loop(collection))
    assert str(caught.value) == "FOR_EACH_DYNAMIC_BOUND_ERROR: static register required"
    assert events == []
    assert context.static_register_sizes is sizes


def test_resource_limit_admits_1024_without_state_allocation(recording):
    context, events, hook = recording
    context.static_register_sizes["reg"] = 1024
    assert hook(context, 0, loop(body=[])) == 1024
    assert len(events) == 1024 and events[-1][2] == ["__foreach_q_1023"]


def test_overflow_rejects_before_callbacks_without_truncation(recording):
    context, events, hook = recording
    context.static_register_sizes["reg"] = 1025
    with pytest.raises(KernelError) as caught:
        hook(context, 0, loop())
    assert str(caught.value) == (
        "STATIC_HILBERT_RESOURCE_ERROR: static Hilbert expansion exceeds the MVP budget (1024)"
    )
    assert events == []


@pytest.mark.parametrize("body", [LitInt(1, SPAN), ExprStmt(LitInt(1, SPAN), SPAN)])
def test_unsupported_body_error_after_first_bind(recording, body):
    context, events, hook = recording
    with pytest.raises(KernelError) as caught:
        hook(context, 0, loop(body=[body]))
    assert str(caught.value) == "forEach body supports Kernel operation calls only"
    assert [e[0] for e in events] == ["bind"]


@pytest.mark.parametrize("bad_call", [
    Call(LitInt(1, SPAN), [Var("H", SPAN), Var("q", SPAN)], SPAN),
    Call(Var("other", SPAN), [Var("H", SPAN), Var("q", SPAN)], SPAN),
    Call(Var("apply", SPAN), [], SPAN),
    Call(Var("apply", SPAN), [Var("H", SPAN)], SPAN),
    Call(Var("apply", SPAN), [Var("H", SPAN), Var("q", SPAN), LitInt(0, SPAN)], SPAN),
    Call(Var("apply", SPAN), [Var("H", SPAN), LitInt(0, SPAN)], SPAN),
    Call(Var("apply", SPAN), [Var("H", SPAN), Var("wrong", SPAN)], SPAN),
], ids=["nonvar", "nonapply", "arity-zero", "arity-one", "arity-three", "nonvar-target", "wrong-element"])
def test_invalid_apply_preserves_error_and_prior_operation(recording, bad_call):
    context, events, hook = recording
    with pytest.raises(KernelError) as caught:
        hook(context, 0, loop(body=[apply(), ExprStmt(bad_call, SPAN)]))
    assert str(caught.value) == "forEach body must apply an operator to its element"
    assert [e[0] for e in events] == ["bind", "apply"]


def test_direct_runtime_literal_register_remains_characterization_only(recording):
    context, events, hook = recording
    assert hook(context, 0, loop(register(LitInt(3, SPAN)))) == 33
    assert len(events) == 6


def test_each_invocation_reads_live_register_map(recording):
    context, events, hook = recording
    assert hook(context, 0, loop(body=[])) == 2
    context.static_register_sizes["reg"] = 1
    events.clear()
    assert hook(context, 0, loop(body=[])) == 1
    assert len(events) == 1


@pytest.mark.parametrize("statement", [Measure(Var("q", SPAN), SPAN), Snapshot(Var("q", SPAN), "out", SPAN)])
def test_runtime_observation_body_is_not_an_operation(recording, statement):
    context, events, hook = recording
    with pytest.raises(KernelError, match="supports Kernel operation calls only"):
        hook(context, 0, loop(body=[statement]))
    assert len(events) == 1
