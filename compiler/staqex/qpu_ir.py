"""Provider-neutral QPU IR inspection projection (LISS-0019 MVP)."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math
import struct
import unicodedata
from types import MappingProxyType
from typing import Any, Iterator, Mapping

from .ast_nodes import (
    BinOp,
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
from .scientific_semantic_ir import (
    ScientificSemanticIR,
    build_scientific_semantic_ir,
    semantic_fingerprint,
)
from .stdlib.prelude import PRELUDE_CONSTANTS
from .static_hilbert import MVP_MAX_LOGICAL_QUBITS

QPU_IR_KIND = "ProviderNeutralQpuIR"
QFT_WIRE_ORDER = "logical"
QPU_GATE_OPCODES = frozenset({"H", "X", "Y", "Z", "S", "T", "CX", "CZ", "RX", "RY", "RZ"})


class QpuCanonicalProjectionError(RuntimeError):
    """Raised when a QPU instruction cannot retain canonical source identity."""


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

    @property
    def source_node_ids(self) -> tuple[str, ...]:
        """Compatibility-free provenance hook for the canonical projection."""
        return tuple(str(item) for item in self.values.get("source_node_ids", ()))

    def __getitem__(self, key: str) -> Any:
        return self.values[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)


def instruction_fingerprint(instructions: tuple[QpuInstruction, ...]) -> str:
    """Digest the executable projection using the canonical byte contract.

    The serializer is deliberately structural: instruction order and duplicate
    operations are significant, strings are NFC-normalized, and non-finite
    numeric values are rejected before an executable artifact can be
    fingerprinted.
    """
    encoded = _canonical_value(
        tuple(_instruction_fingerprint_payload(instruction) for instruction in instructions)
    )
    return hashlib.sha256(encoded).hexdigest()


def _length(value: int) -> bytes:
    """Encode a count or byte length as an unsigned big-endian u64."""
    return struct.pack(">Q", value)


def _canonical_string(value: str) -> bytes:
    normalized = unicodedata.normalize("NFC", value).encode("utf-8")
    return b"S" + _length(len(normalized)) + normalized


def _canonical_value(value: Any) -> bytes:
    """Encode supported fingerprint values with explicit type tags."""
    if value is None:
        return b"N"
    if isinstance(value, bool):
        return b"B" + (b"\x01" if value else b"\x00")
    if isinstance(value, str):
        return _canonical_string(value)
    if isinstance(value, bytes):
        return b"Y" + _length(len(value)) + value
    if isinstance(value, int):
        return b"I" + struct.pack(">q", value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("fingerprint numeric values must be finite")
        if value == 0.0:
            value = 0.0
        return b"F" + struct.pack(">d", value)
    if isinstance(value, complex):
        return b"C" + _canonical_value(float(value.real)) + _canonical_value(float(value.imag))
    if isinstance(value, (tuple, list)):
        return b"A" + _length(len(value)) + b"".join(_canonical_value(item) for item in value)
    if isinstance(value, Mapping):
        entries = [(_canonical_value(key), _canonical_value(item)) for key, item in value.items()]
        entries.sort(key=lambda pair: pair[0])
        return b"M" + _length(len(entries)) + b"".join(
            key + item for key, item in entries
        )
    raise TypeError(f"unsupported fingerprint value: {type(value).__name__}")


def _instruction_fingerprint_payload(instruction: QpuInstruction) -> tuple[Any, ...]:
    provenance = instruction.provenance
    source_node_id = provenance.get("source_node_id")
    provenance_fields = (
        source_node_id,
        provenance.get("role"),
        provenance.get("type"),
        provenance.get("dimensions"),
        provenance.get("exactness"),
        provenance.get("intent"),
    )
    provenance_digest = hashlib.sha256(_canonical_value(provenance_fields)).digest()
    return (
        source_node_id,
        instruction.opcode,
        instruction.qubits,
        instruction.parameter,
        provenance.get("role"),
        provenance.get("type"),
        provenance.get("dimensions"),
        provenance.get("exactness"),
        provenance.get("intent"),
        provenance_digest,
    )


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


def _qft_projection(
    unit: CompilationUnit, semantic_ir: ScientificSemanticIR | None = None
) -> dict[str, Any] | None:
    if semantic_ir is None or semantic_ir.qpu_projection is None:
        return None
    operations = [
        {
            "operation": str(operation.provenance_map().get("source", operation.kind)),
            "source_node_id": operation.source_node_id,
            "size": operation.size,
            "inverse": operation.inverse,
            "control": operation.control,
            "target_offset": operation.target_offset,
        }
        for operation in semantic_ir.qpu_projection.operations
        if operation.kind in {"qft", "cqft"}
    ]
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


def _canonical_node_for_provenance(
    provenance: Mapping[str, Any], semantic_ir: ScientificSemanticIR
) -> str | None:
    """Resolve a lowered instruction back to its source-derived node."""
    line = provenance.get("line")
    col = provenance.get("col")
    matches = [
        node.node_id
        for node in semantic_ir.nodes
        if node.provenance[1] == line and node.provenance[2] == col
    ]
    return matches[-1] if matches else None


def _attach_canonical_provenance(
    instructions: tuple[QpuInstruction, ...], semantic_ir: ScientificSemanticIR
) -> tuple[QpuInstruction, ...]:
    """Annotate every emitted instruction with its canonical source node."""
    attached: list[QpuInstruction] = []
    canonical_ids = {node.node_id for node in semantic_ir.nodes}
    for instruction in instructions:
        source_node_id = instruction.provenance.get("source_node_id")
        if source_node_id not in canonical_ids:
            source_node_id = _canonical_node_for_provenance(instruction.provenance, semantic_ir)
        if source_node_id is None:
            raise QpuCanonicalProjectionError(
                "instruction provenance does not resolve to a Scientific Semantic IR node"
            )
        provenance = dict(instruction.provenance)
        provenance["source_node_id"] = source_node_id
        if instruction.opcode != "Measure":
            provenance.setdefault("comment", f"canonical {instruction.opcode}")
        attached.append(
            QpuInstruction(
                opcode=instruction.opcode,
                qubits=instruction.qubits,
                parameter=instruction.parameter,
                provenance=MappingProxyType(provenance),
            )
        )
    return tuple(attached)


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


def _instruction_projection(
    unit: CompilationUnit, semantic_ir: ScientificSemanticIR
) -> tuple[QpuInstruction, ...]:
    """Lower canonical QPU operation intents without re-reading the AST."""
    projection = semantic_ir.qpu_projection
    if projection is None:
        return ()
    if projection.projection_error is not None:
        return ()
    instructions: list[QpuInstruction] = []
    for operation in projection.operations:
        provenance = MappingProxyType(operation.provenance_map())
        if operation.kind == "gate" and operation.opcode is not None:
            instructions.append(
                QpuInstruction(
                    opcode=operation.opcode,
                    qubits=operation.qubits,
                    parameter=operation.parameter,
                    provenance=provenance,
                )
            )
        elif operation.kind == "measure":
            instructions.append(
                QpuInstruction("Measure", qubits=operation.qubits, provenance=provenance)
            )
        elif operation.kind == "qft" and operation.size is not None:
            span = type("CanonicalSpan", (), {
                "line": provenance.get("line", 0),
                "col": provenance.get("col", 0),
            })()
            instructions.extend(
                _qft_instructions(
                    operation.size,
                    inverse=operation.inverse,
                    span=span,
                    source=str(provenance.get("source", "qft")),
                    target_offset=operation.target_offset,
                )
            )
        elif operation.kind == "cqft" and operation.size is not None:
            span = type("CanonicalSpan", (), {
                "line": provenance.get("line", 0),
                "col": provenance.get("col", 0),
            })()
            instructions.extend(
                _cqft_instructions(
                    operation.size,
                    control=(
                        operation.control
                        if operation.control is not None
                        else operation.size
                    ),
                    inverse=operation.inverse,
                    span=span,
                    source=str(provenance.get("source", "cqft")),
                    target_offset=operation.target_offset,
                )
            )
    return _attach_canonical_provenance(tuple(instructions), semantic_ir)


def _qft_instructions(
    size: int,
    *,
    inverse: bool,
    span: Any,
    source: str,
    target_offset: int = 0,
) -> tuple[QpuInstruction, ...]:
    """Expand exact QFT/IQFT into ADR 0086 basic gates."""
    result: list[QpuInstruction] = []
    provenance = _provenance(span, source)
    targets = (
        range(size - 1 + target_offset, target_offset - 1, -1)
        if inverse
        else range(target_offset, size + target_offset)
    )
    for target in targets:
        controls = (
            range(size - 1 + target_offset, target, -1)
            if inverse
            else range(target + 1, size + target_offset)
        )
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
        left += target_offset
        right += target_offset
        result.extend(_swap_instructions(left, right, provenance))
    return tuple(result)


def _cqft_instructions(
    size: int,
    *,
    control: int,
    inverse: bool,
    span: Any,
    source: str,
    target_offset: int = 0,
) -> tuple[QpuInstruction, ...]:
    """Lift exact QFT/IQFT under one filled control (ADR 0120)."""
    base = _qft_instructions(
        size,
        inverse=inverse,
        span=span,
        source=source,
        target_offset=target_offset,
    )
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


def _hilbert_shape(
    unit: CompilationUnit, semantic_ir: ScientificSemanticIR | None = None
) -> Mapping[str, Any]:
    system = _multi_register_system(unit)
    if system is not None:
        registers = system.registers
        logical_qubits = sum(width for _name, width in registers)
        shape = MappingProxyType(
            {
                "logical_qubits": logical_qubits,
                "hilbert_dimension": 2**logical_qubits,
            }
        )
        return shape
    if semantic_ir is not None and semantic_ir.qpu_projection is not None:
        logical_qubits = semantic_ir.qpu_projection.logical_qubits
        if semantic_ir.qpu_projection.projection_error is not None:
            return MappingProxyType({"logical_qubits": logical_qubits, "hilbert_dimension": None})
        if logical_qubits:
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


def build_qpu_ir(
    unit: CompilationUnit, semantic_ir: ScientificSemanticIR | None = None
) -> QpuProgram:
    """Build the immutable provider-neutral boundary without provider lowering."""
    semantic_ir = semantic_ir or build_scientific_semantic_ir(unit)
    canonical_operations = semantic_ir.qpu_projection.operations if semantic_ir.qpu_projection else ()
    measurement = {"terminal": any(operation.kind == "measure" for operation in canonical_operations)}
    if measurement["terminal"]:
        measurement["operation"] = "Measure"
    projection_error: str | None = (
        semantic_ir.qpu_projection.projection_error
        if semantic_ir.qpu_projection is not None
        else None
    )
    if projection_error is None and semantic_ir.projection_errors:
        projection_error = semantic_ir.projection_errors[0]
    if projection_error is not None:
        # A rejected projection is atomic: no executable or terminal
        # instruction may remain visible to direct QPU consumers.
        instructions = ()
    else:
        try:
            instructions = _instruction_projection(unit, semantic_ir)
        except QpuCanonicalProjectionError as exc:
            instructions = ()
            projection_error = f"E_QPU_CANONICAL_PROVENANCE: {exc}"
    projection = {
        "kind": QPU_IR_KIND,
        "semantic_schema": semantic_ir.schema,
        "semantic_authority": semantic_ir.authority,
        "semantic_relations": semantic_ir.relations,
        "canonical_semantic_ir": semantic_ir,
        "semantic_fingerprint": semantic_fingerprint(semantic_ir),
        "source_node_ids": tuple(node.node_id for node in semantic_ir.nodes),
        "provenance": [node.provenance for node in semantic_ir.nodes],
        "parameters": _parameter_projection(unit),
        "measurement": measurement,
        "hilbert_shape": _hilbert_shape(unit, semantic_ir),
        "instructions": instructions,
        "instruction_fingerprint": instruction_fingerprint(instructions),
        "projection_error": projection_error,
        "projection_errors": semantic_ir.projection_errors,
        "binder_source_node_ids": semantic_ir.binder_source_node_ids,
        "binder_provenance": semantic_ir.binder_provenance,
    }
    multi_register = _multi_register_projection(unit)
    if multi_register is not None:
        projection.update(multi_register)
    qft = _qft_projection(unit, semantic_ir)
    if qft is not None:
        projection["qft"] = qft
    lowering_policy = semantic_ir.lowering_policy
    if lowering_policy is not None:
        projection["lowering_policy"] = lowering_policy
    explicit_evolution = semantic_ir.explicit_evolution
    if explicit_evolution is not None:
        projection["explicit_evolution"] = explicit_evolution
    binder_lowering = semantic_ir.binder_lowering
    if binder_lowering:
        projection["binder_lowering"] = binder_lowering
    return QpuProgram(MappingProxyType(projection))


def qpu_ir_diagnostics(
    unit: CompilationUnit,
    semantic_ir: ScientificSemanticIR | None = None,
) -> list[dict[str, Any]]:
    diagnostics = _qpu_diagnostics(unit)
    semantic_ir = semantic_ir or build_scientific_semantic_ir(unit)
    for code in semantic_ir.projection_errors:
        if not (
            code.startswith("BINDER_")
            or code.startswith("E_QPU_CANONICAL_")
            or code.startswith("E_ALGORITHM_PLAN_CANONICAL_PROVENANCE")
        ):
            continue
        diagnostic_code, _, reason = code.partition(":")
        diagnostic = {
            "code": diagnostic_code,
            "message": "canonical projection rejected this QPU capability",
        }
        if reason:
            diagnostic["reason"] = reason
        diagnostics.append(diagnostic)
    return diagnostics
