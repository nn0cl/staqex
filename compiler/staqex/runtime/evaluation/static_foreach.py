"""Static register expansion using the Evaluator's live state and callbacks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...ast_nodes import Call, ExprStmt, ForEachStmt, KetLit, LitInt, Var
from ...static_hilbert import MVP_MAX_LOGICAL_QUBITS
from .calls import bind_call
from .errors import KernelError

if TYPE_CHECKING:
    from ..joint import Joint
    from .context import EvaluatorContext


def execute_static_foreach(
    context: EvaluatorContext, joint: Joint, stmt: ForEachStmt
) -> Joint:
    """Expand in member/body order without copying evaluator-owned state."""
    collection = stmt.collection
    if isinstance(collection, Var):
        count = context.static_register_sizes.get(collection.name)
    elif (
        isinstance(collection, Call)
        and isinstance(collection.callee, Var)
        and collection.callee.name == "register"
        and len(collection.args) == 1
        and isinstance(collection.args[0], LitInt)
        and collection.args[0].value > 0
    ):
        count = collection.args[0].value
    else:
        count = None
    if count is None or count <= 0:
        raise KernelError("FOR_EACH_DYNAMIC_BOUND_ERROR: static register required")
    if count > MVP_MAX_LOGICAL_QUBITS:
        raise KernelError(
            "STATIC_HILBERT_RESOURCE_ERROR: static Hilbert expansion exceeds "
            f"the MVP budget ({MVP_MAX_LOGICAL_QUBITS})"
        )
    for index in range(count):
        wire = f"__foreach_{stmt.element}_{index}"
        joint = context._bind_names(
            joint,
            [wire],
            KetLit(label="0", span=stmt.span),
            logs=[],
            inspect_out=None,
        )
        for body_stmt in stmt.body.stmts:
            if not isinstance(body_stmt, ExprStmt) or not isinstance(body_stmt.expr, Call):
                raise KernelError("forEach body supports Kernel operation calls only")
            call = body_stmt.expr
            if (
                not isinstance(call.callee, Var)
                or call.callee.name != "apply"
                or len(call.args) != 2
                or not isinstance(call.args[1], Var)
                or call.args[1].name != stmt.element
            ):
                raise KernelError("forEach body must apply an operator to its element")
            expanded = Call(
                callee=call.callee,
                args=[call.args[0], Var(name=wire, span=stmt.span)],
                span=call.span,
            )
            joint = bind_call(context, joint, wire, expanded)
    return joint
