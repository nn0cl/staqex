"""Operator-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from typing import Any, Mapping

from ...ast_nodes import (
    AssignStmt, Attr, BinOp, Call, Expr, FunDecl, OpAttr, OpBin, OpBinder,
    LitFloat, OpCall, OpIdentity, OpIndexed, OpLit, OpPauli, OpPow, OpVar,
    ReturnStmt, SetComprehension,
    StateBind, Var,
)
from .context import EvaluatorContext
from .errors import KernelError
from ..op_attr_elaboration import (
    OpAttrElaborationError, materialize_op_attrs, materialize_op_scalar_vars,
)
from .values import evaluate_value
from ...continuous_lowering import GridHamiltonianRef
from ...second_quantization import SecondQuantizationMappingError, resolve_mapping_expr


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




def _is_numeric(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def _numeric_fields(fields: Mapping[str, Any]) -> dict[str, float]:
    """Return the numeric portion of a receiver's field environment."""
    return {name: float(value) for name, value in fields.items() if _is_numeric(value)}


def operator_name(context, expr: Expr) -> str:
    if isinstance(expr, Var):
        return expr.name
    raise KernelError("hamiltonian / observable must be a named operator (X,Y,Z,…)")

def looks_like_operator_rhs(context, expr: Expr) -> bool:
    """ADR 0180: heuristic for untyped Operator algebra binds."""
    if isinstance(
        expr, (OpVar, OpBin, OpLit, OpBinder, OpIndexed, OpCall, OpAttr, OpPauli)
    ):
        return True
    if isinstance(expr, BinOp) and expr.op in {"+", "-", "*"}:
        return looks_like_operator_rhs(
            context, expr.lhs
        ) or looks_like_operator_rhs(context, expr.rhs)
    if isinstance(expr, Var) and expr.name in {"X", "Y", "Z", "I", "H"}:
        return True
    if isinstance(expr, Call) and isinstance(expr.callee, Var):
        if expr.callee.name in context._function_environment():
            return False
    return False

def resolve_operator(
    context,
    expr: Any,
    *,
    objects: Mapping[str, Any] | None = None,
    extra_arrays: Mapping[str, Any] | None = None,
) -> Any:
    """Resolve an explicit Operator value/factory without leaking locals.

    `objects` (LISS-0410): the struct/class-instance context `OpAttr`
    resolution should use. Defaults to `context._object_environment()` (module scope);
    `resolve_operator_factory_call` passes its own param-name-rekeyed
    `attr_objects` here for a factory function's own local `Operator`
    binds, so `c.defect` resolves against the callee's parameter `c`,
    not a same-named (or absent) module-level object.
    `extra_arrays` (LISS-0434): a factory's own param-name-rekeyed
    `Float[N]…` arrays -- needed here (not only in the caller's later
    `_materialize_op` pass) once a scalar-parameterized binder domain
    (e.g. `Sigma (i In 0..n-1)` where `n` is this call's own scalar
    parameter) makes this same call eagerly lower the binder's body
    too, instead of leaving it for the deferred pass.
    """
    if isinstance(expr, OpVar) and expr.name in context._grid_hamiltonian_environment():
        return GridHamiltonianRef(expr.name)
    if isinstance(expr, Var) and expr.name in context._grid_hamiltonian_environment():
        return GridHamiltonianRef(expr.name)
    if isinstance(expr, OpVar) and expr.name in context._operator_environment():
        return context._operator_environment()[expr.name]
    if isinstance(expr, Var) and expr.name in context._operator_environment():
        return context._operator_environment()[expr.name]
    if isinstance(expr, Call) and isinstance(expr.callee, Var):
        fun = context._function_environment().get(expr.callee.name)
        if fun is not None:
            return resolve_operator_factory_call(context, expr, fun)
    # LISS-0139: Operator H = recv.method(…)
    if isinstance(expr, Call) and isinstance(expr.callee, Attr):
        return resolve_operator_method_call(context, expr)
    return lower_operator_value(
        context, expr, objects=objects, extra_arrays=extra_arrays
    )

def operator_array_context(context) -> dict[str, Any]:
    """Merged Float[N]… coefficient arrays (literal + Host-resolved,
    ADR 0119/LISS-0406) visible at `main` level, for binder lowering
    anywhere an Operator AST needs it (LISS-0407)."""
    from ...finite_binder import _collect_float_arrays

    unit = context._compilation_unit()
    if unit is None:
        return {}
    arrays = dict(_collect_float_arrays(unit))
    host_arrays = getattr(context, "_resolved_host_arrays", None) or {}
    arrays.update(host_arrays)
    return arrays

def resolve_op_call(context, call: "OpCall") -> Any:
    """Inline a call to a known Operator-returning function found
    anywhere inside an Operator expression tree, not only when it is
    the entire right-hand side (LISS-0407, closes the LISS-0402
    "Operator-Call-inline" gap: `scale * f(weights)` previously
    raised `cannot compile sparse Pauli for OpCall`).

    A call to anything else (e.g. binder-internal `next`/`wrap`
    helpers, LISS-0373) is left untouched -- those are resolved by a
    separate, unrelated mechanism inside binder lowering."""
    fun = context._function_environment().get(call.name)
    if fun is None or fun.return_type is None or fun.return_type.name != "Operator":
        return call
    call_args = [
        expr_arg_to_source_expr(a, call.name) for a in call.args
    ]
    synthetic = Call(
        callee=Var(name=call.name, span=call.span),
        args=call_args,
        span=call.span,
    )
    return resolve_operator_factory_call(context, synthetic, fun)

def resolve_operator_tree(
    context,
    expr: Any,
    *,
    arrays: Mapping[str, Any],
    objects: Mapping[str, Any] | None = None,
) -> Any:
    """Single recursive resolution pass over an Operator AST
    (LISS-0407 / ADR 0206, completed LISS-0410): resolves `OpAttr`
    struct-field coefficients, inlines Operator-returning function
    calls found anywhere in the tree, then lowers any remaining
    finite binder against the merged array context. Preserves
    object identity when a subtree needs no change.

    LISS-0410: `OpAttr` used to be resolved by a separate, bolted-on
    call (`materialize_op_attrs`) reachable only from `evolve`'s own
    call site and the factory-call path -- `apply`/`capply`
    (`_resolve_unitary_matrix`) read `context._operator_environment()[name]` directly
    with no resolution step at all, so a struct-field coefficient
    that already worked for `evolve` still failed for `apply`/
    `capply`. Folding `OpAttr` in here makes every `Operator`
    StateBind fully resolved by the time it's stored, so any later
    consumer that just reads `context._operator_environment()[name]` sees a clean
    tree for free."""
    from ...finite_binder import _contains_binder, _lower_operator_expr
    from ..op_attr_elaboration import OpAttrElaborationError, _op_attr_float

    resolved_objects = context._object_environment() if objects is None else objects

    if isinstance(expr, OpAttr):
        try:
            value = _op_attr_float(expr, resolved_objects)
        except OpAttrElaborationError as exc:
            raise KernelError(str(exc)) from exc
        return OpLit(value=float(value), span=expr.span)
    if isinstance(expr, OpCall):
        resolved = resolve_op_call(context, expr)
        if resolved is expr:
            return expr
        return resolve_operator_tree(context, resolved, arrays=arrays, objects=objects)
    if isinstance(expr, OpBin):
        new_lhs = resolve_operator_tree(context, expr.lhs, arrays=arrays, objects=objects)
        new_rhs = resolve_operator_tree(context, expr.rhs, arrays=arrays, objects=objects)
        if new_lhs is expr.lhs and new_rhs is expr.rhs:
            return expr
        return OpBin(op=expr.op, lhs=new_lhs, rhs=new_rhs, span=expr.span)
    if isinstance(expr, OpPow):
        new_base = resolve_operator_tree(context, expr.base, arrays=arrays, objects=objects)
        if new_base is expr.base:
            return expr
        return OpPow(base=new_base, exp=expr.exp, span=expr.span)
    if isinstance(expr, OpBinder):
        # LISS-0430: `Sigma (x In F) { |x><x| }` -- F is a named `Set`
        # variable, not an Index/{0,1}^n domain, so the static
        # `_lower_operator_expr` pass (bounded-integer-range only)
        # cannot resolve it and already skips it (ValueError, caught
        # upstream in `lower_finite_binder_operators`). Resolved here
        # instead, where F's already-computed value is reachable.
        if expr.kind == "Sigma" and isinstance(expr.domain, OpVar):
            looked_up = lookup_set_comprehension_value(context, expr.domain.name)
            if looked_up is not None:
                set_value, domain_width = looked_up
                return build_projector_sum_operator(
                    set_value, expr.variable, expr.body, domain_width
                )
        unit = context._compilation_unit()
        if unit is None:
            return expr
        try:
            if not _contains_binder(expr):
                return expr
        except TypeError:
            return expr
        try:
            return _lower_operator_expr(expr, unit, arrays=arrays)
        except (IndexError, ValueError) as exc:
            raise KernelError(f"cannot lower Operator binder: {exc}") from exc
    return expr

def lookup_set_comprehension_value(
    context, name: str
) -> tuple[tuple[Any, ...], int] | None:
    """LISS-0430: find `name`'s defining `Set name = { ... }` statement
    in `main()` and re-evaluate its comprehension directly. Set
    comprehensions are pure/deterministic (LISS-0429's own bound
    variable never touches per-World data), so re-evaluating here --
    rather than threading the live `Joint` through the whole Operator-
    resolution call chain just to read one already-computed,
    world-independent value back out of it -- gives the identical
    answer with far less invasive plumbing. Also returns the domain's
    own `n` (needed to materialize the empty-`F` identity below, since
    an empty `elements` tuple carries no pattern to infer it from)."""
    from ...ast_nodes import SetPowerDomain

    unit = context._compilation_unit()
    if unit is None or unit.main is None:
        return None
    for stmt in unit.main.body.stmts:
        if (
            isinstance(stmt, StateBind)
            and stmt.names == [name]
            and stmt.ty is not None
            and stmt.ty.name == "Set"
            and isinstance(stmt.expr, SetComprehension)
        ):
            elements = context._evaluate_set_comprehension(stmt.expr, {})
            domain = stmt.expr.domain
            width = (
                int(evaluate_value(context, domain.width, {}))
                if isinstance(domain, SetPowerDomain)
                else 0
            )
            return elements, width
    return None

def lower_operator_value(
    context,
    expr: Any,
    *,
    extra_arrays: Mapping[str, Any] | None = None,
    objects: Mapping[str, Any] | None = None,
) -> Any:
    """Resolve an Operator AST's remaining non-literal nodes (struct
    fields, nested Operator-returning calls, finite binders) via
    `resolve_operator_tree` (LISS-0407/LISS-0410 unifies what used
    to be several separate, bolted-on passes into one recursive
    resolver)."""
    if expr is None or isinstance(expr, (GridHamiltonianRef, str)):
        return expr
    arrays = operator_array_context(context)
    if extra_arrays:
        arrays.update(extra_arrays)
    return resolve_operator_tree(context, expr, arrays=arrays, objects=objects)

def resolve_operator_factory_call(context, expr: Call, fun: FunDecl) -> Any:
    """Evaluate a `fn … -> Operator` Call into a materialized OpExpr.

    LISS-0297: object (struct/class) params bind under **parameter** names so
    ``return coeffs.congestion * Z[0]`` elaborates even when the caller
    passed a differently named outer object (``drive_h(k)``).
    """
    local_scalars: dict[str, float] = {}
    local_ops: dict[str, Any] = {}
    # Param-name → ClassInstance | StructValue for OpAttr elaboration.
    local_objects: dict[str, Any] = {}
    # Param-name → Float[N]… array (LISS-0407): closes the gap where a
    # Float[N] array threaded as a function parameter and indexed
    # inside that function's own `sum` binder body never reached the
    # binder-lowering pass (`cannot compile sparse Pauli for OpBinder`).
    local_arrays: dict[str, Any] = {}
    caller_arrays = operator_array_context(context)
    if len(expr.args) != len(fun.params):
        raise KernelError(
            f"`{fun.name}` expects {len(fun.params)} args, "
            f"got {len(expr.args)}"
        )
    for param, arg in zip(fun.params, expr.args):
        if param.ty is not None and param.ty.name == "Operator":
            continue
        if (
            param.ty is not None
            and param.ty.name == "Float"
            and len(param.ty.args) >= 1
            and isinstance(arg, Var)
            and arg.name in caller_arrays
        ):
            local_arrays[param.name] = caller_arrays[arg.name]
            continue
        # Object params (struct/class) — map under the parameter name.
        if isinstance(arg, Var) and arg.name in context._object_environment():
            local_objects[param.name] = context._object_environment()[arg.name]
            continue
        try:
            local_scalars[param.name] = float(evaluate_value(context, arg, {}))
        except (KernelError, TypeError, ValueError):
            if isinstance(arg, Var) and arg.name in context._scalar_environment():
                local_scalars[param.name] = float(context._scalar_environment()[arg.name])
    # Attr / classical eval frame: free-fn locals prefer param-bound objects.
    local_assign: dict[str, Any] = dict(local_objects)
    local_assign.update(local_scalars)
    attr_objects: dict[str, Any] = dict(context._object_environment())
    attr_objects.update(local_objects)

    def _fold_scalars_and_attrs(raw: Any) -> Any:
        folded = materialize_op_scalar_vars(
            raw,
            local_scalars,
            local_operators=local_ops,
        )
        try:
            folded = materialize_op_attrs(
                folded, attr_objects, operators=context._operator_environment()
            )
        except OpAttrElaborationError as exc:
            raise KernelError(str(exc)) from exc
        return folded

    def _materialize_op(raw: Any) -> Any:
        folded = _fold_scalars_and_attrs(raw)
        return lower_operator_value(context, folded, extra_arrays=local_arrays)

    for stmt in fun.body.stmts:
        if not isinstance(stmt, StateBind) or stmt.ty is None:
            continue
        if stmt.ty.name == "Operator" and len(stmt.names) == 1:
            # LISS-0410: resolve against this call's own param-name
            # object scope (attr_objects), not module-level
            # context._object_environment() -- a factory-local `Operator H = c.field *
            # ...` must see the callee's own parameter `c`.
            # LISS-0434: fold this call's own scalar params/struct
            # attrs (e.g. a width `n` used as a Sigma binder's own
            # `0..n-1` range bound, or `w.activity` as a per-term
            # coefficient inside the binder body, not just as an
            # already-built Operator's outer scale) BEFORE resolving
            # -- `_resolve_operator_expr` eagerly lowers the whole
            # binder (domain and body) in one static pass, which fails
            # closed on an unresolved name/OpAttr rather than
            # deferring; substituting first, the same way `body`/
            # `guard` are already substituted by `_map_op_tree`, avoids
            # that instead of only folding the (already-crashed)
            # result afterward.
            pre_folded = _fold_scalars_and_attrs(stmt.expr)
            raw = resolve_operator(
                context,
                pre_folded,
                objects=attr_objects,
                extra_arrays=local_arrays,
            )
            local_ops[stmt.names[0]] = _materialize_op(raw)
            continue
        if (
            stmt.ty.name
            not in {
                "State",
                "Operator",
                "Delta",
                "POVM",
                "DensityState",
                "QubitRegister",
            }
            and stmt.ty.name not in context._class_environment()
            and stmt.ty.name not in context._struct_environment()
            and stmt.ty.name not in context._enum_environment()
            and len(stmt.names) == 1
        ):
            # Closed globals, or Attr on a free-fn object param (local_objects).
            expr_closed = context._is_closed(stmt.expr)
            if (
                not expr_closed
                and isinstance(stmt.expr, Attr)
                and isinstance(stmt.expr.obj, Var)
                and stmt.expr.obj.name in local_objects
            ):
                expr_closed = True
            if not expr_closed:
                continue
            try:
                local_scalars[stmt.names[0]] = float(
                    evaluate_value(context, stmt.expr, local_assign)
                )
                local_assign[stmt.names[0]] = local_scalars[stmt.names[0]]
            except (KernelError, TypeError, ValueError):
                pass
    result = next(
        (stmt.expr for stmt in fun.body.stmts if isinstance(stmt, ReturnStmt)),
        fun.body.result,
    )
    if isinstance(result, (Var, OpVar)) and result.name in local_ops:
        return lower_operator_value(context, local_ops[result.name])
    if result is not None and not isinstance(result, (Var, OpVar)):
        return _materialize_op(result)
    return expr

def resolve_operator_method_call(context, expr: Call) -> Any:
    """Evaluate `recv.method(…)` returning Operator (LISS-0139)."""
    callee = expr.callee
    if not isinstance(callee, Attr):
        return expr
    recv_expr = callee.obj
    method_name = callee.name
    inst = context._resolve_receiver_instance(recv_expr)
    if inst is None:
        raise KernelError(
            f"Operator method call requires a bound receiver "
            f"(got `{type(recv_expr).__name__}`)"
        )
    if getattr(inst, "class_name", None) is None:
        raise KernelError(
            f"Operator method `{method_name}` requires a class instance"
        )
    classes = context._class_environment()
    cls = classes.get(inst.class_name) or classes.get(inst.class_name.split(".")[-1])
    if cls is None:
        raise KernelError(f"unknown class `{inst.class_name}`")
    method = next((m for m in cls.methods if m.name == method_name), None)
    if method is None:
        raise KernelError(
            f"class `{inst.class_name}` has no method `{method_name}`"
        )
    if method.return_type is None or method.return_type.name != "Operator":
        raise KernelError(
            f"method `{method_name}` must return Operator for "
            f"`Operator … = recv.{method_name}(…)`"
        )
    # Evaluate method body with `this` = receiver; reuse factory scalar fold.
    prev_this = context._current_receiver()
    context._set_current_receiver(inst)
    try:
        local_scalars: dict[str, float] = {}
        local_ops: dict[str, Any] = {}
        # Seed scalars from instance fields (this.J → Float J pattern).
        for fname, fval in inst.fields.items():
            try:
                local_scalars[fname] = float(fval)
            except (TypeError, ValueError):
                pass
        if len(expr.args) != len(method.params):
            raise KernelError(
                f"`{method_name}` expects {len(method.params)} args, "
                f"got {len(expr.args)}"
            )
        for param, arg in zip(method.params, expr.args):
            if param.ty is not None and param.ty.name == "Operator":
                continue
            try:
                local_scalars[param.name] = float(evaluate_value(context, arg, {}))
            except (KernelError, TypeError, ValueError):
                if isinstance(arg, Var) and arg.name in context._scalar_environment():
                    local_scalars[param.name] = float(context._scalar_environment()[arg.name])
        for stmt in method.body.stmts:
            if isinstance(stmt, ReturnStmt):
                continue
            if isinstance(stmt, AssignStmt):
                context._execute_assignment(stmt)
                local_scalars.update(_numeric_fields(inst.fields))
                continue
            if not isinstance(stmt, StateBind) or stmt.ty is None:
                continue
            if stmt.ty.name == "Operator" and len(stmt.names) == 1:
                raw = stmt.expr
                # Resolve this.field / local Float into OpLit via scalars.
                local_ops[stmt.names[0]] = lower_operator_value(
                    context,
                    materialize_op_scalar_vars(
                        raw,
                        {**_numeric_fields(inst.fields), **local_scalars},
                        local_operators=local_ops,
                    ),
                )
                continue
            if stmt.ty.name == "Float" and len(stmt.names) == 1:
                try:
                    local_scalars[stmt.names[0]] = float(
                        evaluate_value(context, stmt.expr, {})
                    )
                except (KernelError, TypeError, ValueError):
                    pass
        result = next(
            (
                stmt.expr
                for stmt in method.body.stmts
                if isinstance(stmt, ReturnStmt)
            ),
            method.body.result,
        )
        field_scalars = _numeric_fields(inst.fields)
        merged = {**field_scalars, **local_scalars}
        if isinstance(result, (Var, OpVar)) and result.name in local_ops:
            return lower_operator_value(
                context,
                materialize_op_scalar_vars(
                    local_ops[result.name], merged, local_operators=local_ops
                ),
            )
        if result is not None and not isinstance(result, (Var, OpVar)):
            return lower_operator_value(
                context,
                materialize_op_scalar_vars(
                    result, merged, local_operators=local_ops
                ),
            )
        raise KernelError(
            f"method `{method_name}` did not return an Operator"
        )
    finally:
        context._set_current_receiver(prev_this)

def bind_second_quantized(context, name: str, family: str, expr: Any) -> None:
    """Bind a typed second-quantized local (LISS-0032, ADR 0093).

    `FermionOperator`/`BosonOperator`/`SpinOperator` locals are kept
    symbolic (no classical value, no numeric mapping yet). A
    `QubitOperator` bind whose expr is `map(op, JordanWigner)` resolves
    the referenced `FermionOperator` through the Jordan-Wigner mapping
    into an ordinary Pauli OpExpr, stored in `context._operator_environment()` exactly
    like a hand-written `Operator` bind so `evolve`/`apply` need no
    special-casing downstream.
    """
    if family == "QubitOperator":
        try:
            mapped_expr = resolve_mapping_expr(
                expr,
                context._second_quantized_environment(),
                context._scalar_environment(),
                context._object_environment(),
            )
        except SecondQuantizationMappingError as exc:
            raise KernelError(f"{exc.code}: {exc.message}") from exc
        if mapped_expr is not None:
            context._operator_environment()[name] = mapped_expr
            return
    context._second_quantized_environment()[name] = expr
