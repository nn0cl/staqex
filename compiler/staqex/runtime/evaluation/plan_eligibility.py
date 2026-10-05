"""Pure eligibility and runtime-unit projection policy for canonical plans.

The functions in this module inspect immutable AST/plan payloads only.  They
do not own evaluator state, semantic authority, or execution side effects.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable

from ...ast_nodes import (
    Attr,
    Call,
    ClassDecl,
    CompilationUnit,
    EvolveExpr,
    FunDecl,
    Measure,
    OpAttr,
    OpBin,
    OpBinder,
    OpCall,
    OpIndexed,
    OpPauli,
    OpPow,
    StateBind,
    Var,
)
from .evolution_ops import explicit_propagator


def is_deferred_callable_eligible(unit: CompilationUnit) -> bool:
    """Keep callable deferral inside the currently closed scope boundary."""

    class_names = {
        declaration.qualified_name
        for declaration in unit.decls
        if isinstance(declaration, ClassDecl)
    }
    class_short_names = {name.rsplit(".", 1)[-1] for name in class_names}
    if unit.main is None:
        return False
    for declaration in unit.decls:
        if not isinstance(declaration, FunDecl) or declaration.name == "main":
            continue
        if any(
            statement.ty is not None
            and statement.ty.name == "Operator"
            and operator_expr_contains_attr(statement.expr)
            for statement in declaration.body.stmts
            if isinstance(statement, StateBind)
        ):
            return False
    for statement in unit.main.body.stmts:
        if not isinstance(statement, StateBind):
            continue
        expression = statement.expr
        if not isinstance(expression, Call):
            continue
        callee = expression.callee
        if isinstance(callee, Var) and callee.name in class_short_names:
            return False
        if isinstance(callee, Attr) and callee.name in class_short_names:
            return False
    return True


def operator_expr_contains_attr(expr: Any) -> bool:
    """Return whether an operator expression depends on an attribute lookup."""

    if isinstance(expr, OpAttr):
        return True
    if isinstance(expr, OpBin):
        return operator_expr_contains_attr(expr.lhs) or operator_expr_contains_attr(
            expr.rhs
        )
    if isinstance(expr, OpPow):
        return operator_expr_contains_attr(expr.base)
    if isinstance(expr, OpBinder):
        return any(
            operator_expr_contains_attr(child)
            for child in (expr.domain, expr.guard, expr.body)
        )
    if isinstance(expr, OpIndexed):
        return operator_expr_contains_attr(expr.base) or operator_expr_contains_attr(
            expr.index
        )
    if isinstance(expr, OpCall):
        return any(operator_expr_contains_attr(arg) for arg in expr.args)
    return False


def is_minimal_local_evolution(unit: CompilationUnit) -> bool:
    """Keep Operator/Hamiltonian setup bounded to the first local slice."""

    if unit.main is None:
        return False
    evolution_count = 0
    for statement in unit.main.body.stmts:
        if isinstance(statement, Measure):
            continue
        if not isinstance(statement, StateBind):
            return False
        if statement.ty is not None and statement.ty.name == "Operator":
            if not isinstance(statement.expr, OpPauli) and explicit_propagator(statement.expr) is None:
                return False
            continue
        if isinstance(statement.expr, EvolveExpr):
            evolution_count += 1
            continue
        return False
    return evolution_count == 1


def is_first_runtime_family(
    unit: CompilationUnit,
    plan: Any,
    *,
    deferred_eligible: Callable[[list[Any]], bool] | None = None,
) -> bool:
    """Return whether the unit is covered by the bounded first family."""

    from ...scientific_semantic_ir import RuntimeExecutionPlan

    if not isinstance(plan, RuntimeExecutionPlan) or unit.main is None:
        return False
    statements = unit.main.body.stmts
    if deferred_eligible is None:
        from .observation import _main_deferred_eligible

        deferred_eligible = _main_deferred_eligible
    if not deferred_eligible(statements):
        return False
    plan_kinds = {node.kind for node in plan.nodes}
    return "StateBind" in plan_kinds and "Measure" in plan_kinds


def project_runtime_unit(
    unit: CompilationUnit, *, drop_operator_declarations: bool = False
) -> CompilationUnit:
    """Project compile-time Operator declarations out of a runtime payload."""

    if not drop_operator_declarations:
        return unit
    assert unit.main is not None
    return replace(
        unit,
        main=replace(
            unit.main,
            body=replace(
                unit.main.body,
                stmts=[
                    statement
                    for statement in unit.main.body.stmts
                    if not (
                        isinstance(statement, StateBind)
                        and statement.ty is not None
                        and statement.ty.name == "Operator"
                    )
                ],
            ),
        ),
    )


def unit_without_operator_declarations(unit: CompilationUnit) -> CompilationUnit:
    """Build the runtime payload without compile-time Operator declarations."""
    return project_runtime_unit(unit, drop_operator_declarations=True)


def evolution_runtime_unit(unit: CompilationUnit) -> CompilationUnit:
    """Keep compile-time Operator declarations out of evolution bind steps."""

    return unit_without_operator_declarations(unit)


def binder_runtime_unit(unit: CompilationUnit) -> CompilationUnit:
    """Retain source Operator declarations for deferred binder materialization."""

    return unit
