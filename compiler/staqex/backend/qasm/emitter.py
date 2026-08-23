"""QASM3Emitter — Circuit → OpenQASM 3.0 text."""

from __future__ import annotations

from dataclasses import dataclass

from ...ast_nodes import CompilationUnit
from ...qpu_ir import (
    QpuProgram,
    build_qpu_ir,
    instruction_fingerprint,
    qpu_ir_diagnostics,
)
from ...scientific_semantic_ir import (
    MIXTURE_PROJECTION_REJECTION_CODE,
    ScientificSemanticIR,
)
from ...scientific_semantic_ir import build_scientific_semantic_ir, semantic_fingerprint
from ...resource_enforcement import enforce_optional_budget
from ...resource_profile import ResourceProfile, SimulationResourceEstimate
from .circuit import Circuit, Gate
from .lower import lower_unit_to_circuit, qudit_capability_reject
from .router import route_circuit
from .topology import Topology, grid, linear

_QASM_GATE_NAMES = {
    "H": "h",
    "X": "x",
    "Y": "y",
    "Z": "z",
    "S": "s",
    "T": "t",
    "CX": "cx",
    "CZ": "cz",
    "RX": "rx",
    "RY": "ry",
    "RZ": "rz",
}


def _source_scalar_bindings(unit: CompilationUnit) -> dict[str, float]:
    """Resolve closed classical scalar bindings for rotation emission."""
    if unit.main is None:
        return {}
    bindings: dict[str, float] = {}
    for statement in unit.main.body.stmts:
        names = getattr(statement, "names", ())
        value = getattr(getattr(statement, "expr", None), "value", None)
        if len(names) == 1 and isinstance(value, (int, float)):
            bindings[names[0]] = float(value)
    return bindings


@dataclass
class EmitResult:
    qasm: str
    notes: list[str]
    ok: bool
    circuit: Circuit | None = None


def _empty_rejection_circuit(
    code: str,
    *,
    provenance: dict[str, object] | None = None,
) -> Circuit:
    """Create the single empty envelope used by every target rejection."""
    return Circuit(
        n_qubits=0,
        n_bits=0,
        gates=[],
        reject_code=code,
        provenance=provenance,
        allocation_started=False,
        allocated_qubits=(),
        partial_program=None,
    )


class QASM3Emitter:
    def __init__(
        self,
        *,
        topology: str | Topology = "linear",
        route: bool = True,
        n_physical: int | None = None,
    ) -> None:
        self.topology_spec = topology
        self.route = route
        self.n_physical = n_physical

    def emit_unit(
        self,
        unit: CompilationUnit,
        *,
        semantic_ir: ScientificSemanticIR | None = None,
        resource_profile: ResourceProfile | None = None,
        resource_estimate: SimulationResourceEstimate | None = None,
    ) -> EmitResult:
        if semantic_ir is not None and semantic_ir.source_unit_identity != id(unit):
            return EmitResult(
                qasm="",
                notes=[
                    "E_QPU_CANONICAL_PROVENANCE: supplied semantic IR does not "
                    "belong to the supplied compilation unit"
                ],
                ok=False,
                circuit=_empty_rejection_circuit("E_QPU_CANONICAL_PROVENANCE"),
            )
        decision = enforce_optional_budget(
            resource_profile,
            resource_estimate,
            lane="qasm",
        )
        if decision is not None:
            if not decision.continue_execution:
                notes = [str(diagnostic.get("message", "")) for diagnostic in decision.diagnostics]
                return EmitResult(
                    qasm="",
                    notes=notes,
                    ok=False,
                    circuit=_empty_rejection_circuit(
                        "EVOLUTION_TARGET_UNSUPPORTED",
                        provenance={
                            "reason": "resource_budget_exceeded_before_allocation",
                            "source_evidence": {
                                "logical_qubits": resource_estimate.logical_qubits,
                                "estimated_bytes": resource_estimate.estimated_bytes,
                                "memory_limit_bytes": resource_profile.simulator.memory_limit_bytes,
                            },
                            "target_plan": None,
                        },
                    ),
                )
        rejected = qudit_capability_reject(unit)
        if rejected is not None:
            return EmitResult(
                qasm="",
                notes=list(rejected.notes),
                ok=False,
                circuit=rejected,
            )
        semantic_ir = semantic_ir or build_scientific_semantic_ir(unit)
        canonical = build_qpu_ir(unit, semantic_ir)
        qpu_result = self._emit_from_qpu_ir_when_available(
            canonical,
            parameter_values=_source_scalar_bindings(unit),
        )
        if qpu_result is not None:
            return qpu_result
        has_executable_instructions = any(
            instruction.opcode != "Measure"
            for instruction in canonical.get("instructions", ())
        )
        if has_executable_instructions:
            return EmitResult(
                qasm="",
                notes=[
                    "E_QPU_CANONICAL_FINITE_PROJECTION_UNAVAILABLE: canonical "
                    "instructions cannot be emitted without a matching projection"
                ],
                ok=False,
                circuit=_empty_rejection_circuit(
                    "E_QPU_CANONICAL_FINITE_PROJECTION_UNAVAILABLE",
                    provenance={
                        "reason": "canonical_instruction_projection_unavailable",
                        "target_plan": None,
                    },
                ),
            )
        if canonical.get("lowering_policy") is not None or canonical.get(
            "binder_lowering"
        ):
            return EmitResult(
                qasm="",
                notes=[
                    "E_QPU_CANONICAL_FINITE_PROJECTION_UNAVAILABLE: finite "
                    "canonical projection produced no executable instructions"
                ],
                ok=False,
                circuit=_empty_rejection_circuit(
                    "E_QPU_CANONICAL_FINITE_PROJECTION_UNAVAILABLE",
                    provenance={
                        "reason": "canonical_instruction_projection_unavailable",
                        "target_plan": None,
                    },
                ),
            )
        diagnostics = qpu_ir_diagnostics(
            unit,
            canonical.get("canonical_semantic_ir"),
        )
        if diagnostics:
            first = diagnostics[0]
            diagnostic_code = str(first.get("code", ""))
            if diagnostic_code.startswith("E_ALGORITHM_PLAN_CANONICAL_PROVENANCE"):
                diagnostic_code = "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
            source_node_id = next(
                (
                    node.node_id
                    for node in semantic_ir.nodes
                    if node.kind == "Limit"
                ),
                "",
            )
            return EmitResult(
                qasm="",
                notes=[str(first.get("message", first.get("code", "")))],
                ok=False,
                circuit=_empty_rejection_circuit(
                    diagnostic_code or "E_QPU_UNSUPPORTED_CAPABILITY",
                    provenance={
                        "reason": "missing_finite_realization"
                        if source_node_id
                        else "canonical_projection_rejected",
                        "source_node_id": source_node_id,
                        "target_plan": None,
                    },
                ),
            )
        if canonical.get("explicit_evolution") is None:
            code = "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
            message = (
                "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE: no executable "
                "canonical QPU projection is available"
            )
        else:
            code = "E_QPU_CANONICAL_PROVENANCE"
            message = (
                "E_QPU_CANONICAL_PROVENANCE: no executable canonical "
                "ordinary-gate projection is available"
            )
        return EmitResult(
            qasm="",
            notes=[message],
            ok=False,
            circuit=_empty_rejection_circuit(code),
        )

    def emit_qpu_program(
        self,
        program: QpuProgram,
        *,
        parameter_values: dict[str, float] | None = None,
    ) -> EmitResult:
        """Consume the immutable provider-neutral QPU IR directly."""
        validation_error = self._validate_canonical_qpu_program(program)
        if validation_error is not None:
            projection_error = str(program.get("projection_error", ""))
            if projection_error.startswith("E_ALGORITHM_PLAN_CANONICAL_PROVENANCE"):
                source_node_id = next(
                    (
                        node.node_id
                        for node in getattr(program.get("canonical_semantic_ir"), "nodes", ())
                        if node.kind == "Limit"
                    ),
                    "",
                )
                return EmitResult(
                    qasm="",
                    notes=validation_error.notes,
                    ok=False,
                    circuit=_empty_rejection_circuit(
                        "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE",
                        provenance={
                            "reason": "missing_finite_realization",
                            "source_node_id": source_node_id,
                            "target_plan": None,
                        },
                    ),
                )
            if projection_error.startswith(f"{MIXTURE_PROJECTION_REJECTION_CODE}:"):
                _code, _separator, reason = projection_error.partition(":")
                canonical = program.get("canonical_semantic_ir")
                mixture = next(
                    (
                        node
                        for node in getattr(canonical, "nodes", ())
                        if node.kind == "WhenExpr"
                    ),
                    None,
                )
                branch_ids = tuple(
                    node.node_id
                    for node in getattr(canonical, "nodes", ())
                    if node.kind == "WhenArm"
                    and mixture is not None
                    and node.node_id in mixture.child_source_node_ids
                )
                provenance = {
                    "reason": reason,
                    "target_plan": None,
                    "source_node_id": mixture.node_id if mixture is not None else "",
                    "branch_source_node_ids": branch_ids,
                    "source_span": {
                        "line": mixture.provenance.line if mixture is not None else 0,
                        "col": mixture.provenance.col if mixture is not None else 0,
                    },
                }
                return EmitResult(
                    qasm="",
                    notes=validation_error.notes,
                    ok=False,
                    circuit=_empty_rejection_circuit(
                        MIXTURE_PROJECTION_REJECTION_CODE,
                        provenance=provenance,
                    ),
                )
            return validation_error
        shape = program["hilbert_shape"]
        n_qubits = int(shape.get("logical_qubits", 0)) or 1
        resolved_values = dict(parameter_values or {})
        declared_parameters = {
            str(item.get("name")) for item in program.get("parameters", ())
        }
        gates: list[Gate] = []
        for instruction in program["instructions"]:
            if instruction.opcode == "Measure":
                gates.append(
                    Gate(
                        "measure",
                        instruction.qubits or (0,),
                        bits=(0,),
                        comment="terminal Measure",
                    )
                )
                continue
            name = _QASM_GATE_NAMES.get(instruction.opcode)
            if name is None:
                return EmitResult(
                    qasm="",
                    notes=[
                        "E_QPU_UNSUPPORTED_CAPABILITY: "
                        f"opcode `{instruction.opcode}` is not supported by OpenQASM"
                    ],
                    ok=False,
                    circuit=_empty_rejection_circuit(
                        "E_QPU_UNSUPPORTED_CAPABILITY",
                        provenance={
                            "reason": "unsupported_opcode",
                            "source_node_id": instruction.provenance.get("source_node_id", ""),
                            "target_plan": None,
                        },
                    ),
                )
            angle = instruction.parameter if name in {"rx", "ry", "rz"} else None
            if isinstance(angle, str) and angle in resolved_values:
                angle = float(resolved_values[angle])
            elif isinstance(angle, str) and angle not in declared_parameters:
                reason = "parameter_unresolved"
                return EmitResult(
                    qasm="",
                    notes=[
                        f"QASM_ROTATION_ANGLE_UNRESOLVED: {reason}: {angle}"
                    ],
                    ok=False,
                    circuit=_empty_rejection_circuit(
                        "QASM_ROTATION_ANGLE_UNRESOLVED",
                        provenance={
                            "reason": reason,
                            "source_node_id": instruction.provenance.get(
                                "source_node_id", ""
                            ),
                        },
                    ),
                )
            gates.append(
                Gate(
                    name,  # type: ignore[arg-type]
                    instruction.qubits,
                    angle=angle,
                    comment=str(
                        instruction.provenance.get(
                            "comment", f"QPU IR {instruction.opcode}"
                        )
                    ),
                )
            )
        logical = Circuit(n_qubits=n_qubits, n_bits=1, gates=gates)
        circ = route_circuit(logical, self._resolve_topo(n_qubits)) if self.route else logical
        declared = list(program.get("parameters", ()))
        symbolic = [
            param
            for param in declared
            if param["name"] not in resolved_values
        ]
        return EmitResult(
            qasm=self.render(circ, parameters=symbolic),
            notes=list(circ.notes),
            ok=True,
            circuit=circ,
        )

    @staticmethod
    def _validate_canonical_qpu_program(program: QpuProgram) -> EmitResult | None:
        """Reject caller-created or provenance-incomplete QPU projections."""
        if program.get("semantic_schema") != "ssc-semantic-v1":
            message = "E_QPU_CANONICAL_PROVENANCE: missing Scientific Semantic IR schema"
        elif program.get("semantic_authority") != "scientific_semantic_ir":
            message = "E_QPU_CANONICAL_PROVENANCE: QPU IR is not owned by Scientific Semantic IR"
        elif program.get("projection_error"):
            message = str(program["projection_error"])
        else:
            canonical = program.get("canonical_semantic_ir")
            if canonical is None:
                message = "E_QPU_CANONICAL_PROVENANCE: canonical semantic IR body is missing"
                canonical = None
            elif tuple(node.node_id for node in canonical.nodes) != program.source_node_ids:
                message = "E_QPU_CANONICAL_PROVENANCE: source node IDs do not match canonical IR"
                canonical = None
            elif [node.provenance for node in canonical.nodes] != list(program["provenance"]):
                message = "E_QPU_CANONICAL_PROVENANCE: provenance does not match canonical IR"
                canonical = None
            elif semantic_fingerprint(canonical) != program.get("semantic_fingerprint"):
                message = "E_QPU_CANONICAL_PROVENANCE: canonical semantic body fingerprint mismatch"
                canonical = None
            if canonical is None:
                return EmitResult(
                    qasm="",
                    notes=[message],
                    ok=False,
                    circuit=_empty_rejection_circuit("E_QPU_CANONICAL_PROVENANCE"),
                )
            source_node_ids = set(program.source_node_ids)
            if instruction_fingerprint(tuple(program.get("instructions", ()))) != program.get(
                "instruction_fingerprint"
            ):
                message = (
                    "E_QPU_CANONICAL_PROVENANCE: executable projection "
                    "fingerprint mismatch"
                )
                return EmitResult(
                    qasm="",
                    notes=[message],
                    ok=False,
                    circuit=_empty_rejection_circuit("E_QPU_CANONICAL_PROVENANCE"),
                )
            canonical_operations = getattr(canonical.qpu_projection, "operations", ())
            finite_gate_projection = any(
                operation.kind == "gate"
                and operation.provenance_map().get("source") == "Evolve.Suzuki"
                for operation in canonical_operations
            )
            expected_gates = tuple(
                (
                    operation.opcode,
                    operation.qubits,
                    operation.parameter,
                    operation.provenance_map(),
                )
                for operation in canonical_operations
                if (
                    operation.kind == "gate"
                    and operation.opcode is not None
                    and operation.provenance_map().get("source") == "Evolve.Suzuki"
                )
            )
            actual_gates = tuple(
                (
                    instruction.opcode,
                    instruction.qubits,
                    instruction.parameter,
                    dict(instruction.provenance),
                )
                for instruction in program.get("instructions", ())
                if (
                    instruction.opcode != "Measure"
                    and instruction.provenance.get("source") == "Evolve.Suzuki"
                )
            )
            if finite_gate_projection and expected_gates and actual_gates != expected_gates:
                message = (
                    "E_QPU_CANONICAL_PROVENANCE: executable instructions do not "
                    "match canonical gate operations"
                )
                return EmitResult(
                    qasm="",
                    notes=[message],
                    ok=False,
                    circuit=_empty_rejection_circuit("E_QPU_CANONICAL_PROVENANCE"),
                )
            expected_measurements = tuple(
                (
                    "Measure",
                    operation.qubits,
                    operation.parameter,
                    operation.provenance_map(),
                )
                for operation in canonical_operations
                if operation.kind == "measure"
            )
            actual_measurements = tuple(
                (
                    instruction.opcode,
                    instruction.qubits,
                    instruction.parameter,
                    dict(instruction.provenance),
                )
                for instruction in program.get("instructions", ())
                if instruction.opcode == "Measure"
            )
            if expected_measurements != actual_measurements:
                message = (
                    "E_QPU_CANONICAL_PROVENANCE: executable measurements do not "
                    "match canonical measurement operations"
                )
                return EmitResult(
                    qasm="",
                    notes=[message],
                    ok=False,
                    circuit=_empty_rejection_circuit("E_QPU_CANONICAL_PROVENANCE"),
                )
            missing = [
                instruction.opcode
                for instruction in program.get("instructions", ())
                if instruction.provenance.get("source_node_id") not in source_node_ids
            ]
            if not missing:
                return None
            message = (
                "E_QPU_CANONICAL_PROVENANCE: instruction lacks a canonical "
                f"source node ({', '.join(missing)})"
            )
        reject_code = (
            message.split(":", 1)[0]
            if str(message).startswith("E_")
            else "E_QPU_CANONICAL_PROVENANCE"
        )
        return EmitResult(
            qasm="",
            notes=[message],
            ok=False,
            circuit=_empty_rejection_circuit(reject_code),
        )

    def _emit_from_qpu_ir_when_available(
        self,
        program: QpuProgram,
        *,
        parameter_values: dict[str, float] | None = None,
    ) -> EmitResult | None:
        if program.get("projection_error"):
            return self.emit_qpu_program(program, parameter_values=parameter_values)
        instructions = tuple(
            instruction
            for instruction in program.get("instructions", ())
            if instruction.opcode != "Measure"
        )
        if not instructions:
            return None
        return self.emit_qpu_program(program, parameter_values=parameter_values)

    def _resolve_topo(self, n_logical: int) -> Topology:
        n = self.n_physical or n_logical
        n = max(n, n_logical)
        if isinstance(self.topology_spec, Topology):
            return self.topology_spec
        spec = self.topology_spec.lower()
        if spec.startswith("grid"):
            # grid-2x2 or grid
            if "x" in spec:
                try:
                    _, rc = spec.split("-", 1)
                    r, c = rc.split("x")
                    return grid(int(r), int(c))
                except ValueError:
                    pass
            side = max(2, int(n**0.5) + (0 if int(n**0.5) ** 2 >= n else 1))
            return grid(side, side)
        return linear(n)

    def render(
        self,
        circ: Circuit,
        *,
        parameters: list[dict[str, str]] | None = None,
    ) -> str:
        lines = [
            "OPENQASM 3.0;",
            'include "stdgates.inc";',
            "// Staqex QASM3Emitter (Phase 4.1)",
        ]
        for param in parameters or []:
            lines.append(f"input float {param['name']};")
        lines.extend(
            [
                f"qubit[{circ.n_qubits}] q;",
                f"bit[{max(circ.n_bits, 1)}] c;",
            ]
        )
        for g in circ.gates:
            lines.append(self._fmt_gate(g))
        lines.append("")
        return "\n".join(lines)

    def _fmt_gate(self, g: Gate) -> str:
        cmt = f"  // {g.comment}" if g.comment else ""
        if g.name == "h":
            return f"h q[{g.qubits[0]}];{cmt}"
        if g.name == "x":
            return f"x q[{g.qubits[0]}];{cmt}"
        if g.name == "y":
            return f"y q[{g.qubits[0]}];{cmt}"
        if g.name == "z":
            return f"z q[{g.qubits[0]}];{cmt}"
        if g.name == "s":
            return f"s q[{g.qubits[0]}];{cmt}"
        if g.name == "t":
            return f"t q[{g.qubits[0]}];{cmt}"
        if g.name in {"rx", "ry", "rz"}:
            if g.angle is None:
                ang: float | str = 0.0
            else:
                ang = g.angle
            return f"{g.name}({ang}) q[{g.qubits[0]}];{cmt}"
        if g.name == "cx":
            return f"cx q[{g.qubits[0]}], q[{g.qubits[1]}];{cmt}"
        if g.name == "cz":
            return f"cz q[{g.qubits[0]}], q[{g.qubits[1]}];{cmt}"
        if g.name == "swap":
            return f"swap q[{g.qubits[0]}], q[{g.qubits[1]}];{cmt}"
        if g.name == "measure":
            b = g.bits[0] if g.bits else 0
            return f"c[{b}] = measure q[{g.qubits[0]}];{cmt}"
        return f"// unknown gate {g.name}"


def emit_openqasm3(
    unit: CompilationUnit,
    *,
    semantic_ir: ScientificSemanticIR | None = None,
    topology: str = "linear",
    route: bool = True,
) -> EmitResult:
    return QASM3Emitter(topology=topology, route=route).emit_unit(
        unit, semantic_ir=semantic_ir
    )
