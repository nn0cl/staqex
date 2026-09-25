"""Classical evaluation of Operator-expression ASTs and binders."""

from __future__ import annotations

from typing import Any, Mapping, Protocol

from ...ast_nodes import (
    IndexDomain,
    OpBin,
    OpBinder,
    OpIndexed,
    OpLit,
    OpPow,
    OpVar,
    RevDomain,
)
from .errors import KernelError


class ClassicalOperatorContext(Protocol):
    """Read-only access to the Evaluator-owned values used by this family."""

    def _scalar_environment(self) -> Mapping[str, Any]: ...

    def _operator_array_context(self) -> Mapping[str, Any]: ...


def eval_classical_op_binder(
    context: ClassicalOperatorContext, expr: OpBinder, assign: dict[str, Any]
) -> Any:
    """Evaluate classical Sigma/Pi/ForAll/Min binders without owning state."""
    domain = expr.domain
    descending = False
    while isinstance(domain, RevDomain):
        descending = not descending
        domain = domain.inner
    if not isinstance(domain, IndexDomain):
        raise KernelError(
            "classical Sigma/Pi/ForAll requires a bare-range binder "
            "domain (e.g. `0..n-1`), not an Operator/State-shaped domain"
        )

    start = int(eval_op_expr_classical(context, domain.start, assign))
    end = int(eval_op_expr_classical(context, domain.end, assign))
    indices = list(range(start, end + 1)) if end >= start else []
    if descending:
        indices.reverse()

    if expr.kind == "Sigma":
        accumulator: Any = 0
    elif expr.kind == "Pi":
        accumulator = 1
    elif expr.kind == "ForAll":
        accumulator = True
    else:  # Min
        # Preserve the existing fold identity for empty and guarded domains.
        accumulator = float("inf")

    for index in indices:
        local = dict(assign)
        local[expr.variable] = index
        if expr.guard is not None and not bool(
            eval_op_expr_classical(context, expr.guard, local)
        ):
            continue
        if isinstance(expr.body, OpBinder):
            term = eval_classical_op_binder(context, expr.body, local)
        else:
            term = eval_op_expr_classical(context, expr.body, local)

        if expr.kind == "Sigma":
            accumulator = accumulator + term
        elif expr.kind == "Pi":
            accumulator = accumulator * term
        elif expr.kind == "ForAll":
            accumulator = accumulator and bool(term)
            if not accumulator:
                break
        else:  # Min
            accumulator = term if term < accumulator else accumulator

    return accumulator


def eval_op_expr_classical(
    context: ClassicalOperatorContext, expr: Any, assign: dict[str, Any]
) -> Any:
    """Evaluate an Operator expression as a classical value."""
    if isinstance(expr, OpBinder):
        return eval_classical_op_binder(context, expr, assign)
    if isinstance(expr, OpLit):
        return expr.value
    if isinstance(expr, OpVar):
        if expr.name in assign:
            return assign[expr.name]
        if expr.name in context._scalar_environment():
            return context._scalar_environment()[expr.name]
        arrays = context._operator_array_context()
        if expr.name in arrays:
            return arrays[expr.name]
        raise KernelError(f"classical Sigma/Pi: unbound name `{expr.name}`")
    if isinstance(expr, OpIndexed):
        base = eval_op_expr_classical(context, expr.base, assign)
        index = int(eval_op_expr_classical(context, expr.index, assign))
        try:
            return base[index]
        except (TypeError, IndexError, KeyError) as error:
            raise KernelError(
                f"classical Sigma/Pi: index {index} out of range"
            ) from error
    if isinstance(expr, OpPow):
        base = eval_op_expr_classical(context, expr.base, assign)
        return base ** expr.exp
    if isinstance(expr, OpBin):
        if expr.op in ("&&", "||"):
            lhs = bool(eval_op_expr_classical(context, expr.lhs, assign))
            rhs = bool(eval_op_expr_classical(context, expr.rhs, assign))
            return (lhs and rhs) if expr.op == "&&" else (lhs or rhs)
        if expr.op == "Implies":
            lhs = bool(eval_op_expr_classical(context, expr.lhs, assign))
            rhs = bool(eval_op_expr_classical(context, expr.rhs, assign))
            return (not lhs) or rhs

        lhs = eval_op_expr_classical(context, expr.lhs, assign)
        rhs = eval_op_expr_classical(context, expr.rhs, assign)
        operations = {
            "+": lambda left, right: left + right,
            "-": lambda left, right: left - right,
            "*": lambda left, right: left * right,
            "<": lambda left, right: left < right,
            "<=": lambda left, right: left <= right,
            ">": lambda left, right: left > right,
            ">=": lambda left, right: left >= right,
            "==": lambda left, right: left == right,
            "!=": lambda left, right: left != right,
        }
        if expr.op not in operations:
            raise KernelError(
                f"classical Sigma/Pi: unsupported operator `{expr.op}`"
            )
        return operations[expr.op](lhs, rhs)

    raise KernelError(
        f"classical Sigma/Pi body contains a non-classical term "
        f"({type(expr).__name__}) -- Operator/Pauli atoms belong in "
        "an Operator-typed Sigma/Pi, not a classical one"
    )
