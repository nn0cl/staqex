"""Elaborate OpAttr field projections into OpLit (ADR 0114 / LISS-0121).

Keeps Operator DSL ``struct.field * Pauli`` equivalent to a named classical
coefficient after struct construction, without treating the field as a linear
quantum resource.
"""

from __future__ import annotations

from typing import Any, Mapping

from ..ast_nodes import (
    IndexDomain,
    OpAttr,
    OpBin,
    OpBinder,
    OpCall,
    OpExpr,
    OpIndexed,
    OpLit,
    OpPow,
    OpVar,
    RevDomain,
)


class OpAttrElaborationError(ValueError):
    """Struct field could not be elaborated as a numeric Operator coefficient."""


def materialize_op_attrs(
    op: OpExpr,
    objects: Mapping[str, Any],
    *,
    operators: Mapping[str, OpExpr] | None = None,
    _seen: frozenset[str] = frozenset(),
) -> OpExpr:
    """Rewrite ``OpAttr`` nodes to ``OpLit`` using runtime struct field values.

    LISS-0407: when ``operators`` is given, also recurses through an
    ``OpVar`` naming another bound Operator (e.g. ``Operator H = G +
    X[0]`` where ``G``'s own tree still has a raw ``OpAttr`` leaf) --
    closes the indirection gap where a struct-field coefficient hidden
    behind an intermediate named Operator variable never got elaborated.
    ``_seen`` guards against a self-referential Operator name cycle.
    """
    if isinstance(op, OpAttr):
        return OpLit(value=float(_op_attr_float(op, objects)), span=op.span)
    if (
        isinstance(op, OpVar)
        and operators is not None
        and op.name in operators
        and op.name not in _seen
    ):
        return materialize_op_attrs(
            operators[op.name],
            objects,
            operators=operators,
            _seen=_seen | {op.name},
        )
    return _map_op_tree(
        op, lambda child: materialize_op_attrs(child, objects, operators=operators, _seen=_seen)
    )


def materialize_op_scalar_vars(
    op: OpExpr,
    scalars: Mapping[str, float],
    *,
    local_operators: Mapping[str, OpExpr] | None = None,
) -> OpExpr:
    """Rewrite classical ``OpVar`` coefficients to ``OpLit`` (LISS-0136).

    Operator factory functions bind named ``Float`` locals then return an
    Operator AST that still mentions those names. After the call returns, the
    factory locals are gone — fold known scalars (and local Operator aliases)
    before publishing the AST to the caller.
    """
    local_operators = local_operators or {}
    if isinstance(op, OpVar):
        if op.name in scalars:
            return OpLit(value=float(scalars[op.name]), span=op.span)
        if op.name in local_operators:
            return materialize_op_scalar_vars(
                local_operators[op.name],
                scalars,
                local_operators=local_operators,
            )
        return op
    if isinstance(op, OpAttr):
        return op
    return _map_op_tree(
        op,
        lambda child: materialize_op_scalar_vars(
            child, scalars, local_operators=local_operators
        ),
    )


def _map_op_tree(op: OpExpr, map_child) -> OpExpr:
    if isinstance(op, OpBin):
        return OpBin(
            op=op.op,
            lhs=map_child(op.lhs),
            rhs=map_child(op.rhs),
            span=op.span,
        )
    if isinstance(op, OpPow):
        return OpPow(base=map_child(op.base), exp=op.exp, span=op.span)
    if isinstance(op, OpIndexed):
        return OpIndexed(
            base=map_child(op.base),
            index=map_child(op.index),
            span=op.span,
        )
    if isinstance(op, OpBinder):
        return OpBinder(
            kind=op.kind,
            variable=op.variable,
            domain=_map_binder_domain(op.domain, map_child),
            body=map_child(op.body),
            span=op.span,
            guard=None if op.guard is None else map_child(op.guard),
            origin=op.origin,
        )
    if isinstance(op, OpCall):
        return OpCall(
            name=op.name,
            args=[map_child(a) for a in op.args],
            span=op.span,
        )
    return op


def _map_binder_domain(domain: Any, map_child) -> Any:
    """LISS-0434: an `IndexDomain`'s own `start`/`end` (e.g. the `n` in
    `0..n-1`) are OpExpr leaves too -- a scalar factory parameter used as
    a binder's own range bound needs the same fold-before-lowering
    `materialize_op_scalar_vars`/`materialize_op_attrs` already give a
    binder's body/guard, or the static lowering pass that runs after
    folding sees an unresolved name and fails closed. Named-Set domains
    (`OpVar`) and `TypeRef` (`Basis<N>`/literal `Index<N>`) carry no
    OpExpr sub-nodes to fold; left unchanged."""
    if isinstance(domain, IndexDomain):
        return IndexDomain(
            start=map_child(domain.start),
            end=map_child(domain.end),
            span=domain.span,
        )
    if isinstance(domain, RevDomain):
        return RevDomain(
            inner=_map_binder_domain(domain.inner, map_child), span=domain.span
        )
    return domain


def _resolve_op_attr_host(expr: OpExpr, objects: Mapping[str, Any]) -> Any:
    """Resolve OpVar / nested OpAttr to a runtime object with ``.fields``.

    Supports multi-level free-fn coefficients such as ``o.inner.c``
    (LISS-0306 / re-review P1-2).
    """
    if isinstance(expr, OpVar):
        return objects.get(expr.name)
    if isinstance(expr, OpAttr):
        parent = _resolve_op_attr_host(expr.obj, objects)
        fields = getattr(parent, "fields", None)
        if not isinstance(fields, dict) or expr.name not in fields:
            return None
        return fields[expr.name]
    return None


def _op_attr_float(op: OpAttr, objects: Mapping[str, Any]) -> float:
    host = _resolve_op_attr_host(op.obj, objects)
    fields = getattr(host, "fields", None)
    if not isinstance(fields, dict):
        # Nested leaf may itself be a numeric field value (should not reach here
        # for intermediate hosts); fall back to historical error shape.
        if isinstance(op.obj, OpVar):
            raise OpAttrElaborationError(
                f"unbound struct for Operator coefficient `{op.obj.name}.{op.name}`"
            )
        raise OpAttrElaborationError(
            "Operator field projection requires a struct binding "
            f"(got `{type(op.obj).__name__}`)"
        )
    if op.name not in fields:
        label = op.obj.name if isinstance(op.obj, OpVar) else op.name
        raise OpAttrElaborationError(
            f"unknown struct field `{op.name}` on `{label}`"
        )
    raw = fields[op.name]
    try:
        return float(raw)
    except (TypeError, ValueError) as exc:
        raise OpAttrElaborationError(
            f"struct field `.{op.name}` is not a numeric elaboration coefficient"
        ) from exc
