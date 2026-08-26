"""Dynamic reuse/reset capability demand inference (ADR 0199 / LISS-0385;
reset spelling and inference added by the ADR 0199 Amendment / LISS-0390).

``needs_reuse`` is true when a mid-circuit-measured wire is later used as a
quantum target in the same ``dynamic qpu`` block (including ``match``
arms). ``needs_reset`` is true when the block contains a ``reset``
statement (including inside ``match`` arms). Timing ``within`` is ignored.
"""

from __future__ import annotations

from .ast_nodes import (
    Block,
    Call,
    CompilationUnit,
    DynamicQpuStmt,
    ExprStmt,
    MatchStmt,
    MeasureExpr,
    ResetStmt,
    StateBind,
    Var,
)
from .dynamic_qpu import DynamicCapabilityDemand


def infer_dynamic_capability_demand(unit: CompilationUnit) -> DynamicCapabilityDemand:
    """Infer P0 capability demand flags from source AST."""

    needs_reuse = False
    needs_reset = False
    if unit.main is not None:
        for statement in unit.main.body.stmts:
            if isinstance(statement, DynamicQpuStmt):
                if _block_demands_reuse(statement.body):
                    needs_reuse = True
                if _block_demands_reset(statement.body):
                    needs_reset = True
                if needs_reuse and needs_reset:
                    break
    return DynamicCapabilityDemand(
        needs_reset=needs_reset,
        needs_reuse=needs_reuse,
        needs_latency=False,
    )


def _block_demands_reset(block: Block) -> bool:
    for statement in block.stmts:
        if isinstance(statement, ResetStmt):
            return True
        if isinstance(statement, MatchStmt):
            for arm in statement.arms:
                if _block_demands_reset(arm.body):
                    return True
    return False


def reuse_demand_diagnostics(unit: CompilationUnit) -> list[dict[str, object]]:
    """Compile-time soft diagnostics when reuse is demanded on the P0 path."""

    demand = infer_dynamic_capability_demand(unit)
    if not demand.needs_reuse or unit.main is None:
        return []
    dynamic = next(
        (stmt for stmt in unit.main.body.stmts if isinstance(stmt, DynamicQpuStmt)),
        None,
    )
    span = dynamic.span if dynamic is not None else unit.main.span
    return [
        {
            "code": "DYN_CAPABILITY_REUSE",
            "line": span.line,
            "col": span.col,
            "message": (
                "post-measure quantum use of a mid-circuit-measured wire "
                "demands reuse capability (LISS-0388: supported on "
                "simulator-class Fake profiles; a hardware-constrained or "
                "live profile may still reject at verify time)"
            ),
        }
    ]


def _block_demands_reuse(block: Block) -> bool:
    measured_wires: set[str] = set()
    for statement in block.stmts:
        measured = _controller_measure_wire(statement)
        if measured is not None:
            measured_wires.add(measured)
            continue
        if isinstance(statement, MatchStmt):
            for arm in statement.arms:
                if _stmts_target_measured_wires(arm.body.stmts, measured_wires):
                    return True
            continue
        if _stmt_targets_measured_wires(statement, measured_wires):
            return True
    return False


def _controller_measure_wire(statement: object) -> str | None:
    if not isinstance(statement, StateBind):
        return None
    if statement.ty is None or statement.ty.name != "Controller":
        return None
    if not isinstance(statement.expr, MeasureExpr):
        return None
    if not isinstance(statement.expr.expr, Var):
        return None
    return statement.expr.expr.name


def _stmts_target_measured_wires(
    statements: list[object],
    measured_wires: set[str],
) -> bool:
    return any(_stmt_targets_measured_wires(stmt, measured_wires) for stmt in statements)


def _stmt_targets_measured_wires(
    statement: object,
    measured_wires: set[str],
) -> bool:
    if not measured_wires:
        return False
    targets = _quantum_target_wires(statement)
    return bool(targets & measured_wires)


def _quantum_target_wires(statement: object) -> set[str]:
    if isinstance(statement, ExprStmt) and isinstance(statement.expr, Call):
        return _call_quantum_targets(statement.expr)
    if isinstance(statement, StateBind) and isinstance(statement.expr, Call):
        return _call_quantum_targets(statement.expr)
    return set()


def _call_quantum_targets(call: Call) -> set[str]:
    if not isinstance(call.callee, Var):
        return set()
    op = call.callee.name
    args = list(call.args)
    if op == "apply":
        return {arg.name for arg in args[1:] if isinstance(arg, Var)}
    if op == "hadamard":
        return {arg.name for arg in args if isinstance(arg, Var)}
    if op == "toffoli" and args:
        last = args[-1]
        return {last.name} if isinstance(last, Var) else set()
    if op in {"capply", "ocapply", "controlled"}:
        # Targets follow the unitary argument; take trailing Vars after the
        # first non-Var / Operator-like name heuristic: last contiguous Vars.
        targets: list[str] = []
        for arg in reversed(args):
            if isinstance(arg, Var) and arg.name not in {
                "X",
                "Y",
                "Z",
                "H",
                "Hadamard",
                "I",
                "S",
                "T",
            }:
                # Could be control or target; for demand purposes any use of a
                # previously measured wire as a Var operand counts as reuse.
                targets.append(arg.name)
            else:
                break
        return set(targets)
    return set()
