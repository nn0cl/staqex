"""Dynamic-lane execution mechanics extracted from the Evaluator facade."""

from __future__ import annotations

from typing import Any

import cmath

from ...ast_nodes import *  # noqa: F403
from ...measure_sink_port import MeasureSinkPort
from .context import EvaluatorContext
from ..joint import EPS, Joint
from .calls import bind_call


def _run_dynamic_qpu_block(
    context,
    joint: Joint,
    stmt: DynamicQpuStmt,
    *,
    logs: list[str],
    inspect_out: MeasureSinkPort | None,
) -> Joint:
    """LISS-0387 (ADR 0200 Decisions 1-3, 6): real dynamic qpu execution.

    Mid-circuit `Controller<T> = measure wire` performs a genuine
    Lueders projection + renormalize -- the same `project_coord`
    primitive `project(psi, k)` already uses in the Static Kernel, not a
    bookkeeping label. The matching `match` arm then runs against the
    real post-measure joint via the existing Call-statement dispatch.
    Host has already Fake-gated this run by the time this is reached
    (unchanged from LISS-0383); `physical_execution_claimed` semantics
    live entirely in the Host layer and are untouched here.

    LISS-0395: the block body is executed via `_run_dynamic_arm_body`
    (the top level is "the outermost arm body") instead of a second,
    hand-maintained copy of the same statement dispatch -- this is what
    makes a Controller-measure or a wire touched only inside a nested
    `match` arm reach the same real-collapse / block-end trace-out
    treatment as a top-level one, at any nesting depth.
    """
    controller_values: dict[str, str] = {}
    dynamically_measured: list[str] = []

    joint = context._run_dynamic_arm_body(
        joint,
        stmt.body.stmts,
        controller_values,
        dynamically_measured,
        logs=logs,
        inspect_out=inspect_out,
    )

    # LISS-0387 Decision 5: dynamically-measured wires are local to the
    # block (never referenced by the surrounding Static `main`); trace
    # them out here via the already-shipped ADR 0173 primitive instead
    # of relying on Host's LINEAR_IMPLICIT_DISCARD bypass. LISS-0395:
    # `dynamically_measured` is now populated at any nesting depth
    # (including wires only ever touched inside a match arm), since
    # `_run_dynamic_arm_body` mutates this same list by reference.
    for wire in dynamically_measured:
        joint = joint.trace_out(wire)
    return joint

def _reset_dynamic_wire(context, joint: Joint, wire: str, span: Span) -> Joint:
    """LISS-0390: trace_out(wire) then re-prepare wire as |0>.

    Reuses the two already-shipped primitives LISS-0387 (KetLit |0>
    preparation) and ADR 0173 (Joint.trace_out) established -- no new
    Joint math. Deliberately distinct from the Static Kernel's
    same-name `state x = |0>` idiom (LISS-0114 F verification).
    """
    joint = joint.trace_out(wire)
    return context._bind_names(
        joint, [wire], KetLit(label="0", span=span), logs=[], inspect_out=None
    )

def _run_dynamic_arm_body(
    context,
    joint: Joint,
    stmts: list[Any],
    controller_values: dict[str, str] | None = None,
    dynamically_measured: list[str] | None = None,
    *,
    logs: list[str] | None = None,
    inspect_out: MeasureSinkPort | None = None,
) -> Joint:
    """LISS-0395: single recursive statement dispatcher for dynamic-lane
    bodies, used both for the top-level `dynamic qpu` block (via
    `_run_dynamic_qpu_block`) and for `match` arm bodies (including
    arms nested inside arms). `controller_values` and
    `dynamically_measured` are threaded by reference so a
    Controller-measure or a reset performed at any nesting depth is
    visible to sibling/descendant statements and to the caller's
    block-end trace-out accounting, exactly as if it had happened at
    the top level.
    """
    if controller_values is None:
        controller_values = {}
    if dynamically_measured is None:
        dynamically_measured = []
    for body_stmt in stmts:
        if (
            isinstance(body_stmt, StateBind)
            and body_stmt.ty is not None
            and body_stmt.ty.name == "Controller"
            and isinstance(body_stmt.expr, MeasureExpr)
            and isinstance(body_stmt.expr.expr, Var)
            and len(body_stmt.names) == 1
        ):
            wire = body_stmt.expr.expr.name
            controller_name = body_stmt.names[0]
            outcome = context._resolve_dynamic_outcome(controller_name)
            joint = context._collapse_dynamic_wire(joint, wire, outcome)
            controller_values[controller_name] = outcome
            dynamically_measured.append(wire)
            continue
        if isinstance(body_stmt, MatchStmt):
            value = controller_values.get(body_stmt.scrutinee)
            arm = next(
                (a for a in body_stmt.arms if a.pattern == value), None
            )
            if arm is not None:
                joint = context._run_dynamic_arm_body(
                    joint,
                    arm.body.stmts,
                    controller_values,
                    dynamically_measured,
                    logs=logs,
                    inspect_out=inspect_out,
                )
            continue
        if isinstance(body_stmt, ResetStmt):
            # LISS-0390 (ADR 0199 Amendment Decision 7): reuses
            # trace_out (ADR 0173) + KetLit |0> re-preparation -- no
            # new Joint primitive. Tracked for block-end disposal like
            # a measured wire, in case the wire is never touched again.
            joint = context._reset_dynamic_wire(joint, body_stmt.target, body_stmt.span)
            dynamically_measured.append(body_stmt.target)
            continue
        if isinstance(body_stmt, StateBind):
            joint = context._bind_names(
                joint,
                body_stmt.names,
                body_stmt.expr,
                logs=logs,
                inspect_out=inspect_out,
            )
            continue
        if isinstance(body_stmt, ExprStmt) and isinstance(body_stmt.expr, Call):
            joint = context._bind_call( joint, "__dynamic_expr_stmt", body_stmt.expr)
            continue
    return joint

def _resolve_dynamic_outcome(context, controller_name: str) -> str:
    """LISS-0387 Decision 2: supplied-outcome only (no RNG sampling yet)."""
    if context.host_input is not None:
        supplied = context.host_input.get(f"dynamic:{controller_name}")
        if supplied is not None:
            return str(supplied)
    raise context._kernel_error(
        "DYN_SUPPLIED_OUTCOME_MISSING: no Host-supplied outcome for "
        f"controller `{controller_name}` (RNG-sampled dynamic execution "
        "is out of scope for LISS-0387)"
    )

def _collapse_dynamic_wire(context, joint: Joint, wire: str, outcome: str) -> Joint:
    """LISS-0387 Decision 1: Lueders projection + renormalize on `wire`.

    Identical operation to the Static Kernel's `project(psi, k)` --
    reuses `Joint.project_coord`, no new Joint math.
    """
    label: Any = int(outcome) if outcome in {"0", "1"} else outcome
    projected = joint.project_coord(wire, lambda v: v == label)
    if projected.is_vacuum():
        # LISS-0389: the recorded outcome was physically unreachable.
        context._dynamic_outcomes_confirmed = False
        return Joint.empty()
    from ..joint import World, _coalesce

    total = sum(abs(w.amp) ** 2 for w in projected.worlds)
    if total <= EPS:
        context._dynamic_outcomes_confirmed = False
        return Joint.empty()
    scale = 1.0 / cmath.sqrt(total)
    out = [
        World(
            assign=dict(w.assign),
            amp=w.amp * scale,
            coord_phase=dict(w.coord_phase),
        )
        for w in projected.worlds
    ]
    return Joint(worlds=_coalesce(out))
