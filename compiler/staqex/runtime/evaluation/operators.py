"""Operator-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from typing import Any

from ...ast_nodes import Call, LitFloat, OpBin, OpIdentity, OpLit, OpPauli, OpVar, Var
from .context import EvaluatorContext
from .errors import KernelError


def expr_arg_to_source_expr(arg: Any, call_name: str) -> Any:
    """Convert an Operator-call argument to the generic expression shape."""
    if isinstance(arg, OpVar):
        return Var(name=arg.name, span=arg.span)
    if isinstance(arg, OpLit):
        return LitFloat(value=arg.value, span=arg.span)
    raise KernelError(
        f"unsupported argument shape `{type(arg).__name__}` in "
        f"nested Operator call `{call_name}`"
    )


def build_projector_sum_operator(
    elements: tuple[Any, ...],
    bound_variable: str,
    body: Any,
    domain_width: int,
) -> Any:
    """Lower a set-domain projector sum into a literal operator tree."""
    if not (
        isinstance(body, Call)
        and isinstance(body.callee, Var)
        and body.callee.name == "projector"
        and len(body.args) == 1
        and isinstance(body.args[0], Var)
        and body.args[0].name == bound_variable
    ):
        raise KernelError(
            "Sigma (x In F) { ... } over a Set domain requires the "
            "body to be exactly `|x><x|` (the bound variable's own "
            "projector)"
        )
    if not elements:
        return OpIdentity(kind="Sigma", acting_space=domain_width, span=body.span)
    terms: list[Any] = []
    for pattern in elements:
        factors = []
        for i, bit in enumerate(pattern):
            sign = -1.0 if bit else 1.0
            z_term: Any = OpPauli(kind="Z", site=i, span=body.span)
            if sign < 0:
                z_term = OpBin(
                    op="*",
                    lhs=OpLit(value=-1.0, span=body.span),
                    rhs=z_term,
                    span=body.span,
                )
            factors.append(
                OpBin(
                    op="*",
                    lhs=OpLit(value=0.5, span=body.span),
                    rhs=OpBin(
                        op="+",
                        lhs=OpPauli(kind="I", site=i, span=body.span),
                        rhs=z_term,
                        span=body.span,
                    ),
                    span=body.span,
                )
            )
        product = factors[0]
        for factor in factors[1:]:
            product = OpBin(op="*", lhs=product, rhs=factor, span=body.span)
        terms.append(product)
    result = terms[0]
    for term in terms[1:]:
        result = OpBin(op="+", lhs=result, rhs=term, span=body.span)
    return result


def resolve_operator(
    context: EvaluatorContext,
    expr: Any,
    *,
    objects: dict[str, Any] | None = None,
    extra_arrays: dict[str, Any] | None = None,
) -> Any:
    """Delegate operator resolution while preserving evaluator state ownership."""
    return context._legacy_resolve_operator(
        expr, objects=objects, extra_arrays=extra_arrays
    )
