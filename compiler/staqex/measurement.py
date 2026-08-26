"""Static contracts for terminal POVM measurement declarations."""

from __future__ import annotations

from dataclasses import dataclass

from .ast_nodes import Call, CompilationUnit, FunDecl, Measure, StateBind, Var


@dataclass(frozen=True, slots=True)
class POVMContract:
    name: str
    domain: str
    kind: str


def resolve_measurement_contracts(
    unit: CompilationUnit,
) -> tuple[dict[str, POVMContract], list[dict]]:
    if unit.main is None:
        return {}, []
    povms: dict[str, POVMContract] = {}
    states: dict[str, str] = {}
    diagnostics: list[dict] = []
    for statement in unit.main.body.stmts:
        if not isinstance(statement, StateBind) or statement.ty is None:
            continue
        if len(statement.names) != 1:
            continue
        name = statement.names[0]
        if statement.ty.name in {"State", "DensityState"}:
            domain = statement.ty.args[0].name if statement.ty.args else "Unknown"
            states[name] = domain
        elif statement.ty.name == "POVM":
            domain = _declared_domain(statement)
            if not _is_computational_basis(statement.expr):
                diagnostics.append(
                    _diagnostic(
                        "INVALID_POVM_EFFECT",
                        statement,
                        "the MVP POVM constructor is ComputationalBasis()",
                    )
                )
            povms[name] = POVMContract(
                name=name,
                domain=domain,
                kind="ComputationalBasis",
            )
    for statement in unit.main.body.stmts:
        if not isinstance(statement, Measure) or statement.povm is None:
            continue
        if not isinstance(statement.povm, Var) or statement.povm.name not in povms:
            diagnostics.append(
                _diagnostic(
                    "INVALID_POVM_EFFECT",
                    statement,
                    "measurement requires a declared POVM value",
                )
            )
            continue
        source_domain = _measure_source_domain(statement.expr, states, unit)
        if source_domain is not None:
            povm_domain = povms[statement.povm.name].domain
            if source_domain != povm_domain:
                diagnostics.append(
                    _diagnostic(
                        "POVM_DOMAIN_MISMATCH",
                        statement,
                        f"POVM domain `{povm_domain}` does not match `{source_domain}`",
                    )
                )
    return povms, diagnostics


def _measure_source_domain(
    expr: object,
    states: dict[str, str],
    unit: CompilationUnit,
) -> str | None:
    """Domain of a measure target: named bind, or zero-arg Call return type.

    LISS-0377: POVM domain checks used to require ``isinstance(expr, Var)``,
    so ``measure make() with p`` silently skipped ``POVM_DOMAIN_MISMATCH``
    even when ``make`` returned ``DensityState<Qubit>``.
    """
    if isinstance(expr, Var):
        return states.get(expr.name)
    if (
        not isinstance(expr, Call)
        or not isinstance(expr.callee, Var)
        or expr.args
    ):
        return None
    for decl in unit.decls:
        if not isinstance(decl, FunDecl) or decl.name != expr.callee.name:
            continue
        return_type = decl.return_type
        if (
            return_type is not None
            and return_type.name in {"State", "DensityState"}
            and return_type.args
        ):
            return return_type.args[0].name
        return None
    return None


def _is_computational_basis(expr: object) -> bool:
    return (
        isinstance(expr, Call)
        and isinstance(expr.callee, Var)
        and expr.callee.name == "ComputationalBasis"
        and not expr.args
    )


def _declared_domain(statement: StateBind) -> str:
    return statement.ty.args[0].name if statement.ty and statement.ty.args else "Unknown"


def _diagnostic(code: str, statement: StateBind | Measure, message: str) -> dict:
    span = statement.span
    return {"code": code, "line": span.line, "col": span.col, "message": message}
