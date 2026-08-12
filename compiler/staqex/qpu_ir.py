"""Provider-neutral QPU IR inspection projection (LISS-0019 MVP)."""

from __future__ import annotations

from dataclasses import dataclass
import math
from types import MappingProxyType
from typing import Any, Iterator, Mapping

from .ast_nodes import (
    Call,
    CompilationUnit,
    DynamicQpuStmt,
    ExprStmt,
    ForEachStmt,
    EvolveExpr,
    LitFloat,
    LitInt,
    LitString,
    Measure,
    OpExpr,
    ScientificScopeDecl,
    StateBind,
    Var,
)
from .backend.qasm.trotter import (
    TrotterError,
    compile_hamiltonian,
    eval_time_expr,
    resolve_suzuki_order,
    resolve_suzuki_steps,
)
from .finite_binder import lower_finite_binders
from .stdlib.prelude import PRELUDE_CONSTANTS
from .static_hilbert import MVP_MAX_LOGICAL_QUBITS

QPU_IR_KIND = "ProviderNeutralQpuIR"
QFT_WIRE_ORDER = "logical"
QPU_GATE_OPCODES = frozenset({"H", "X", "Y", "Z", "CX", "RX", "RY", "RZ"})


@dataclass(frozen=True)
class QpuInstruction:
    """Immutable provider-neutral instruction in the first QPU vocabulary."""

    opcode: str
    qubits: tuple[int, ...] = ()
    parameter: str | float | None = None
    provenance: Mapping[str, Any] = MappingProxyType({})


@dataclass(frozen=True)
class QpuProgram(Mapping[str, Any]):
    """Immutable in-memory QPU IR root; not a serialization format."""

    values: Mapping[str, Any]

    def __getitem__(self, key: str) -> Any:
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)


def _parameter_projection(unit: CompilationUnit) -> list[dict[str, str]]:
    from .parametric_binding import extract_circuit_parameters

    return [
        {"name": param.name, "domain": param.domain}
        for param in extract_circuit_parameters(unit)
    ]


def _parameter_binding_names(unit: CompilationUnit) -> dict[str, str]:
    """Map local `Param` variable names to external binding keys."""
    if unit.main is None:
        return {}
    names: dict[str, str] = {}
    for stmt in unit.main.body.stmts:
        if not isinstance(stmt, StateBind) or stmt.ty is None or stmt.ty.name != "Param":
            continue
        if len(stmt.names) != 1:
            continue
        local = stmt.names[0]
        binding = local
        if (
            isinstance(stmt.expr, Call)
            and isinstance(stmt.expr.callee, Var)
            and stmt.expr.callee.name == "parameter"
            and len(stmt.expr.args) == 1
            and isinstance(stmt.expr.args[0], LitString)
        ):
            binding = stmt.expr.args[0].value
        names[local] = binding
    return names


def _has_terminal_measure(unit: CompilationUnit) -> bool:
    return bool(
        unit.main is not None
        and any(isinstance(stmt, Measure) for stmt in unit.main.body.stmts)
    )


def _qft_projection(unit: CompilationUnit) -> dict[str, Any] | None:
    if unit.main is None:
        return None
    operations = []
    for stmt in unit.main.body.stmts:
        if not (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Operator"
            and isinstance(stmt.expr, Call)
            and isinstance(stmt.expr.callee, Var)
            and stmt.expr.callee.name in {"qft", "iqft", "cqft", "ciqft"}
        ):
            continue
        operations.append({"name": stmt.names[0], "operation": stmt.expr.callee.name})
    if not operations:
        return None
    return {
        "operations": operations,
        "inverse_of": "qft",
        "wire_order": QFT_WIRE_ORDER,
    }


def _static_register_size(collection: Any, register_sizes: Mapping[str, int]) -> int | None:
    if isinstance(collection, Var):
        return register_sizes.get(collection.name)
    if isinstance(collection, Call) and isinstance(collection.callee, Var):
        if collection.callee.name == "register" and len(collection.args) == 1:
            arg = collection.args[0]
            if isinstance(arg, LitInt) and arg.value > 0:
                return arg.value
    return None


def _provenance(span: Any, source: str) -> Mapping[str, Any]:
    return MappingProxyType({"line": span.line, "col": span.col, "source": source})


def _gate_name(
    expr: Any, param_bindings: dict[str, str] | None = None
) -> tuple[str, str | float | None] | None:
    if isinstance(expr, Var) and expr.name.upper() in QPU_GATE_OPCODES:
        return expr.name.upper(), None
    if isinstance(expr, Call) and isinstance(expr.callee, Var):
        name = expr.callee.name.upper()
        if name in {"RX", "RY", "RZ"} and len(expr.args) == 1:
            arg = expr.args[0]
            if isinstance(arg, (LitInt, LitFloat)):
                return name, float(arg.value)
            if isinstance(arg, Var):
                binding = (param_bindings or {}).get(arg.name, arg.name)
                return name, binding
    return None


def _instruction_projection(unit: CompilationUnit) -> tuple[QpuInstruction, ...]:
    if unit.main is None:
        return ()
    instructions: list[QpuInstruction] = []
    register_sizes: dict[str, int] = {}
    param_bindings = _parameter_binding_names(unit)
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and stmt.ty is not None and stmt.ty.name == "QubitRegister":
            if stmt.names and stmt.ty.args and stmt.ty.args[0].name.isdigit():
                register_sizes[stmt.names[0]] = int(stmt.ty.args[0].name)
    for stmt in unit.main.body.stmts:
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Operator"
            and isinstance(stmt.expr, Call)
            and isinstance(stmt.expr.callee, Var)
            and stmt.expr.callee.name in {"qft", "iqft"}
            and len(stmt.expr.args) == 1
            and isinstance(stmt.expr.args[0], Var)
        ):
            size = register_sizes.get(stmt.expr.args[0].name)
            if size is not None and size <= MVP_MAX_LOGICAL_QUBITS:
                instructions.extend(
                    _qft_instructions(
                        size,
                        inverse=stmt.expr.callee.name == "iqft",
                        span=stmt.span,
                        source=stmt.expr.callee.name,
                    )
                )
            continue
        if (
            isinstance(stmt, StateBind)
            and stmt.ty is not None
            and stmt.ty.name == "Operator"
            and isinstance(stmt.expr, Call)
            and isinstance(stmt.expr.callee, Var)
            and stmt.expr.callee.name in {"cqft", "ciqft"}
            and len(stmt.expr.args) == 2
            and isinstance(stmt.expr.args[0], Var)
            and isinstance(stmt.expr.args[1], Var)
        ):
            ctrl_size = register_sizes.get(stmt.expr.args[0].name)
            size = register_sizes.get(stmt.expr.args[1].name)
            if (
                ctrl_size == 1
                and size is not None
                and ctrl_size + size <= MVP_MAX_LOGICAL_QUBITS
            ):
                instructions.extend(
                    _cqft_instructions(
                        size,
                        control=size,  # control after target wires 0..N-1
                        inverse=stmt.expr.callee.name == "ciqft",
                        span=stmt.span,
                        source=stmt.expr.callee.name,
                    )
                )
            continue
        if isinstance(stmt, ForEachStmt):
            count = _static_register_size(stmt.collection, register_sizes)
            if count is None:
                continue
            for index in range(count):
                for body_stmt in stmt.body.stmts:
                    if not isinstance(body_stmt, ExprStmt) or not isinstance(body_stmt.expr, Call):
                        continue
                    call = body_stmt.expr
                    if not (
                        isinstance(call.callee, Var)
                        and call.callee.name == "apply"
                        and len(call.args) == 2
                    ):
                        continue
                    gate = _gate_name(call.args[0], param_bindings)
                    if gate is None:
                        continue
                    opcode, parameter = gate
                    instructions.append(
                        QpuInstruction(
                            opcode=opcode,
                            qubits=(index,),
                            parameter=parameter,
                            provenance=_provenance(body_stmt.span, "ForEach.apply"),
                        )
                    )
        elif isinstance(stmt, Measure):
            instructions.append(
                QpuInstruction(
                    opcode="Measure",
                    provenance=_provenance(stmt.span, "Measure"),
                )
            )
    return tuple(instructions)


def _qft_instructions(
    size: int,
    *,
    inverse: bool,
    span: Any,
    source: str,
) -> tuple[QpuInstruction, ...]:
    """Expand exact QFT/IQFT into ADR 0086 basic gates."""
    result: list[QpuInstruction] = []
    provenance = _provenance(span, source)
    targets = range(size - 1, -1, -1) if inverse else range(size)
    for target in targets:
        controls = range(size - 1, target, -1) if inverse else range(target + 1, size)
        if not inverse:
            result.append(QpuInstruction("H", (target,), provenance=provenance))
        for control in controls:
            theta = math.pi / (2 ** (control - target))
            result.extend(
                _controlled_phase_instructions(
                    control, target, theta, inverse=inverse, provenance=provenance
                )
            )
        if inverse:
            result.append(QpuInstruction("H", (target,), provenance=provenance))
    for left in range(size // 2):
        right = size - left - 1
        result.extend(_swap_instructions(left, right, provenance))
    return tuple(result)


def _cqft_instructions(
    size: int,
    *,
    control: int,
    inverse: bool,
    span: Any,
    source: str,
) -> tuple[QpuInstruction, ...]:
    """Lift exact QFT/IQFT under one filled control (ADR 0120)."""
    base = _qft_instructions(size, inverse=inverse, span=span, source=source)
    provenance = _provenance(span, source)
    lifted: list[QpuInstruction] = []
    for instruction in base:
        lifted.extend(
            _lift_basic_gate_under_control(control, instruction, provenance=provenance)
        )
    return tuple(lifted)


def _lift_basic_gate_under_control(
    control: int,
    instruction: QpuInstruction,
    *,
    provenance: Mapping[str, Any],
) -> tuple[QpuInstruction, ...]:
    """Decompose controlled-H / controlled-RZ / controlled-CX into basic gates."""
    if instruction.opcode == "H" and len(instruction.qubits) == 1:
        target = instruction.qubits[0]
        quarter = math.pi / 4.0
        return (
            QpuInstruction("RY", (target,), quarter, provenance=provenance),
            QpuInstruction("CX", (control, target), provenance=provenance),
            QpuInstruction("RY", (target,), -quarter, provenance=provenance),
        )
    if instruction.opcode == "RZ" and len(instruction.qubits) == 1:
        target = instruction.qubits[0]
        theta = float(instruction.parameter or 0.0)
        return _controlled_phase_instructions(
            control, target, theta, inverse=False, provenance=provenance
        )
    if instruction.opcode == "CX" and len(instruction.qubits) == 2:
        return _toffoli_basic(
            control, instruction.qubits[0], instruction.qubits[1], provenance
        )
    # Fallback: treat unsupported as identity under control (should not happen).
    return ()


def _toffoli_basic(
    c1: int, c2: int, target: int, provenance: Mapping[str, Any]
) -> tuple[QpuInstruction, ...]:
    """Ancilla-free CCX into H/CX/RZ (T = RZ(π/4))."""
    t_angle = math.pi / 4.0
    return (
        QpuInstruction("H", (target,), provenance=provenance),
        QpuInstruction("CX", (c2, target), provenance=provenance),
        QpuInstruction("RZ", (target,), -t_angle, provenance=provenance),
        QpuInstruction("CX", (c1, target), provenance=provenance),
        QpuInstruction("RZ", (target,), t_angle, provenance=provenance),
        QpuInstruction("CX", (c2, target), provenance=provenance),
        QpuInstruction("RZ", (target,), -t_angle, provenance=provenance),
        QpuInstruction("CX", (c1, target), provenance=provenance),
        QpuInstruction("RZ", (c2,), t_angle, provenance=provenance),
        QpuInstruction("RZ", (target,), t_angle, provenance=provenance),
        QpuInstruction("H", (target,), provenance=provenance),
        QpuInstruction("CX", (c1, c2), provenance=provenance),
        QpuInstruction("RZ", (c1,), t_angle, provenance=provenance),
        QpuInstruction("RZ", (c2,), -t_angle, provenance=provenance),
        QpuInstruction("CX", (c1, c2), provenance=provenance),
    )


def _controlled_phase_instructions(
    control: int,
    target: int,
    theta: float,
    *,
    inverse: bool,
    provenance: Mapping[str, Any],
) -> tuple[QpuInstruction, ...]:
    """Decompose the accepted controlled phase contract into CX/RZ."""
    cx = QpuInstruction("CX", (control, target), provenance=provenance)
    if inverse:
        return (
            cx,
            QpuInstruction("RZ", (target,), theta / 2.0, provenance=provenance),
            cx,
            QpuInstruction("RZ", (target,), -theta / 2.0, provenance=provenance),
        )
    return (
        QpuInstruction("RZ", (target,), theta / 2.0, provenance=provenance),
        cx,
        QpuInstruction("RZ", (target,), -theta / 2.0, provenance=provenance),
        cx,
    )


def _swap_instructions(
    left: int, right: int, provenance: Mapping[str, Any]
) -> tuple[QpuInstruction, ...]:
    """Decompose a register-reversal swap without adding a SWAP opcode."""
    return (
        QpuInstruction("CX", (left, right), provenance=provenance),
        QpuInstruction("CX", (right, left), provenance=provenance),
        QpuInstruction("CX", (left, right), provenance=provenance),
    )


def _hilbert_shape(unit: CompilationUnit) -> Mapping[str, Any]:
    system = _multi_register_system(unit)
    if system is not None:
        registers = system.registers
        logical_qubits = sum(width for _name, width in registers)
        return MappingProxyType(
            {
                "logical_qubits": logical_qubits,
                "hilbert_dimension": 2**logical_qubits,
            }
        )
    if unit.main is None:
        return MappingProxyType({"logical_qubits": 0})
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and stmt.ty is not None and stmt.ty.name == "QubitRegister":
            if stmt.ty.args and stmt.ty.args[0].name.isdigit():
                return MappingProxyType({"logical_qubits": int(stmt.ty.args[0].name)})
    return MappingProxyType({"logical_qubits": 0})


def _multi_register_projection(unit: CompilationUnit) -> Mapping[str, Any] | None:
    system = _multi_register_system(unit)
    if system is None:
        return None
    offset = 0
    logical_registers: list[dict[str, Any]] = []
    logical_qubits: list[dict[str, Any]] = []
    for name, width in system.registers:
        logical_registers.append({"name": name, "width": width, "offset": offset})
        for local_index in range(width):
            logical_qubits.append(
                {
                    "logical_register": name,
                    "logical_index": local_index,
                    "flat_index": offset + local_index,
                }
            )
        offset += width
    return MappingProxyType(
        {
            "acting_space": f"RegisterSet<{system.name}>",
            "logical_registers": logical_registers,
            "logical_qubits": logical_qubits,
            "tensor_order": [name for name, _width in system.registers],
            "tensor_order_provenance": {
                "source": "system register declaration order",
                "registers": [name for name, _width in system.registers],
            },
        }
    )


def _multi_register_system(unit: CompilationUnit) -> ScientificScopeDecl | None:
    """Return the sole declared static system shape, if one exists."""
    systems = [
        declaration
        for declaration in unit.decls
        if isinstance(declaration, ScientificScopeDecl)
        and declaration.kind == "system"
        and declaration.registers
    ]
    if len(systems) > 1:
        # Multiple system declarations require a future explicit composition
        # contract; selecting one would be an implicit fallback.
        return None
    return systems[0] if systems else None


def _qpu_diagnostics(unit: CompilationUnit) -> list[dict[str, Any]]:
    if unit.main is None:
        return []
    diagnostics: list[dict[str, Any]] = []
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and isinstance(stmt.expr, EvolveExpr):
            if stmt.expr.until_predicate is not None:
                diagnostics.append({
                    "code": "E_QPU_UNSUPPORTED_CAPABILITY",
                    "line": stmt.span.line,
                    "col": stmt.span.col,
                    "message": "dynamic evolve-until is not supported by the static QPU IR",
                })
        if isinstance(stmt, DynamicQpuStmt):
            diagnostics.append({
                "code": "E_QPU_UNSUPPORTED_CAPABILITY",
                "line": stmt.span.line,
                "col": stmt.span.col,
                "message": "dynamic QPU control is not supported by the static QPU IR",
            })
    return diagnostics


def _lowering_policy_projection(unit: CompilationUnit) -> dict[str, Any] | None:
    """Project the accepted Suzuki policy and its statically resolved steps."""
    if unit.main is None:
        return None
    binds = [stmt for stmt in unit.main.body.stmts if isinstance(stmt, StateBind)]
    op_env: dict[str, OpExpr] = {}
    scalars: dict[str, float] = {k: float(v) for k, v in PRELUDE_CONSTANTS.items()}
    evolves: list[EvolveExpr] = []
    for stmt in binds:
        if stmt.ty is not None and stmt.ty.name == "Operator" and len(stmt.names) == 1:
            op_env[stmt.names[0]] = stmt.expr  # type: ignore[assignment]
        elif stmt.ty is not None and stmt.ty.name in {"Float", "Int"} and len(stmt.names) == 1:
            if isinstance(stmt.expr, (LitFloat, LitInt)):
                scalars[stmt.names[0]] = float(stmt.expr.value)
        if isinstance(stmt.expr, EvolveExpr) and stmt.expr.suzuki is not None:
            evolves.append(stmt.expr)
    if not evolves:
        return None
    policy = evolves[0].suzuki
    assert policy is not None
    steps: int | None = None
    tolerance: float | None = None
    if isinstance(policy.steps, LitInt):
        steps = int(policy.steps.value)
    if isinstance(policy.tolerance, (LitInt, LitFloat)):
        tolerance = float(policy.tolerance.value)
    if steps is None and tolerance is not None:
        ev = evolves[0]
        if ev.duration is None or ev.hamiltonian is None:
            return None
        try:
            duration = eval_time_expr(ev.duration, scalars)
            terms = compile_hamiltonian(
                ev.hamiltonian,
                env=op_env,
                scalars=scalars,
                n_qubits=max(1, len(ev.seeds)),
            )
            steps = resolve_suzuki_steps(policy, terms, duration, scalars)
        except TrotterError:
            # QPU IR inspection must not replace the compiler's normal
            # lowering diagnostic when the source is not QASM-lowerable.
            return None
    if steps is None:
        return None
    return {
        "algorithm": "Suzuki",
        "order": resolve_suzuki_order(policy.order, scalars),
        "steps": steps,
        "error_mode": policy.error_mode if tolerance is not None else None,
        "tolerance_target": tolerance,
    }


def build_qpu_ir(
    unit: CompilationUnit, symbolic_ir: dict[str, Any]
) -> QpuProgram:
    """Build the immutable provider-neutral boundary without provider lowering."""
    measurement = {"terminal": _has_terminal_measure(unit)}
    if measurement["terminal"]:
        measurement["operation"] = "Measure"
    projection = {
        "kind": QPU_IR_KIND,
        "provenance": symbolic_ir.get("provenance", []),
        "parameters": _parameter_projection(unit),
        "measurement": measurement,
        "hilbert_shape": _hilbert_shape(unit),
        "instructions": _instruction_projection(unit),
    }
    multi_register = _multi_register_projection(unit)
    if multi_register is not None:
        projection.update(multi_register)
    qft = _qft_projection(unit)
    if qft is not None:
        projection["qft"] = qft
    lowering_policy = _lowering_policy_projection(unit)
    if lowering_policy is not None:
        projection["lowering_policy"] = lowering_policy
    binder_lowering, _ = lower_finite_binders(unit)
    if binder_lowering:
        projection["binder_lowering"] = binder_lowering
    return QpuProgram(MappingProxyType(projection))


def qpu_ir_diagnostics(unit: CompilationUnit) -> list[dict[str, Any]]:
    diagnostics = _qpu_diagnostics(unit)
    _, binder_diagnostics = lower_finite_binders(unit)
    diagnostics.extend(binder_diagnostics)
    return diagnostics
