"""OpenQASM 3 emission for the Dynamic QPU lane (ADR 0201, LISS-0391).

Separate from the Static QPU / Parametric circuit emitter (`emitter.py`,
`lower.py`, `circuit.py`) -- those are structurally built for straight-line
gate circuits with no Controller/match/reset concept and no
conditional-block representation. This module walks the Dynamic-lane AST
directly and emits QASM3 text using QASM3's own native vocabulary
(classical `bit`, `if`, `reset`) -- no invented dialect, no shared-IR
extension.

Emission is available whenever the program compiles (ADR 0201 Decision 4)
-- independent of any `dynamic_fake_profile` Host gate. It makes no
`physical_execution_claimed` claim of any kind (ADR 0201 Decision 2): this
is a text transformation, not a submission.
"""

from __future__ import annotations

from dataclasses import dataclass

from ...ast_nodes import (
    Call,
    CompilationUnit,
    DynamicQpuStmt,
    ExprStmt,
    KetLit,
    MatchStmt,
    MeasureExpr,
    ResetStmt,
    StateBind,
    Var,
)

_QASM_GATE_NAMES = {
    "H": "h",
    "X": "x",
    "Y": "y",
    "Z": "z",
    "CX": "cx",
    "RX": "rx",
    "RY": "ry",
    "RZ": "rz",
}


@dataclass
class DynamicEmitResult:
    qasm: str
    notes: list[str]
    ok: bool


def emit_dynamic_qpu_qasm3(unit: CompilationUnit) -> DynamicEmitResult:
    """Emit QASM3 text for the first `dynamic qpu` block in `unit`."""

    if unit.main is None:
        return DynamicEmitResult(qasm="", notes=["no main function"], ok=False)
    dynamic = next(
        (stmt for stmt in unit.main.body.stmts if isinstance(stmt, DynamicQpuStmt)),
        None,
    )
    if dynamic is None:
        return DynamicEmitResult(qasm="", notes=["no dynamic qpu block"], ok=False)

    qubits: list[str] = []
    bits: list[str] = []
    body_lines: list[str] = []
    notes: list[str] = []
    ok = True

    for line in _emit_block(dynamic.body.stmts, qubits, bits, notes):
        body_lines.append(line)
    if notes:
        ok = False

    header = [
        "OPENQASM 3.0;",
        'include "stdgates.inc";',
        "// Staqex dynamic qpu QASM3 emission (ADR 0201 / LISS-0391)",
        "// physical_execution_claimed: N/A -- text emission only, not a submission",
    ]
    for wire in qubits:
        header.append(f"qubit {wire};")
    for controller in bits:
        header.append(f"bit {controller};")

    qasm = "\n".join(header + body_lines) + "\n"
    return DynamicEmitResult(qasm=qasm, notes=notes, ok=ok)


def _emit_block(
    stmts: list[object],
    qubits: list[str],
    bits: list[str],
    notes: list[str],
    *,
    indent: str = "",
) -> list[str]:
    lines: list[str] = []
    for stmt in stmts:
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Controller"
            and isinstance(stmt.expr, MeasureExpr)
            and isinstance(stmt.expr.expr, Var)
            and len(stmt.names) == 1
        ):
            wire = stmt.expr.expr.name
            controller = stmt.names[0]
            if wire not in qubits:
                qubits.append(wire)
            if controller not in bits:
                bits.append(controller)
            lines.append(f"{indent}{controller} = measure {wire};")
            continue
        if (
            isinstance(stmt, StateBind)
            and isinstance(stmt.expr, KetLit)
            and stmt.expr.label == "0"
            and len(stmt.names) == 1
        ):
            wire = stmt.names[0]
            if wire not in qubits:
                qubits.append(wire)
            continue
        if isinstance(stmt, MatchStmt):
            for arm in stmt.arms:
                lines.append(f"{indent}if ({stmt.scrutinee} == {arm.pattern}) {{")
                lines.extend(
                    _emit_block(arm.body.stmts, qubits, bits, notes, indent=indent + "    ")
                )
                lines.append(f"{indent}}}")
            continue
        if isinstance(stmt, ResetStmt):
            if stmt.target not in qubits:
                qubits.append(stmt.target)
            lines.append(f"{indent}reset {stmt.target};")
            continue
        if isinstance(stmt, ExprStmt) and isinstance(stmt.expr, Call):
            rendered = _emit_call(stmt.expr, qubits, notes)
            if rendered is not None:
                lines.append(f"{indent}{rendered}")
            continue
        notes.append(
            f"DYN_QASM_UNSUPPORTED_STMT: {type(stmt).__name__} has no QASM3 "
            "mapping in this Issue's scope"
        )
    return lines


def _emit_call(call: Call, qubits: list[str], notes: list[str]) -> str | None:
    if not isinstance(call.callee, Var) or call.callee.name != "apply":
        return None
    if len(call.args) != 2 or not isinstance(call.args[0], Var):
        return None
    op = call.args[0].name
    target = call.args[1]
    name = _QASM_GATE_NAMES.get(op)
    if name is None or not isinstance(target, Var):
        notes.append(f"DYN_QASM_UNSUPPORTED_GATE: `{op}` has no QASM3 mapping")
        return None
    if target.name not in qubits:
        qubits.append(target.name)
    return f"{name} {target.name};"
