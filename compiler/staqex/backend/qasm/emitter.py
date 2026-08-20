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
from ...scientific_semantic_ir import ScientificSemanticIR
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


@dataclass
class EmitResult:
    qasm: str
    notes: list[str]
    ok: bool
    circuit: Circuit | None = None


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
                circuit=Circuit(
                    n_qubits=1,
                    n_bits=1,
                    reject_code="E_QPU_CANONICAL_PROVENANCE",
                ),
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
                    circuit=Circuit(
                        n_qubits=max(resource_estimate.logical_qubits, 1),
                        n_bits=1,
                        reject_code="SIMULATOR_RESOURCE_ERROR",
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
        qpu_result = self._emit_from_qpu_ir_when_available(canonical)
        if qpu_result is not None:
            return qpu_result
        # A finite Suzuki/binder projection still uses the established finite
        # lowering implementation until its instruction projection is moved
        # in a separately reviewed slice. Unresolved ideal evolution never
        # enters this compatibility boundary.
        if canonical.get("lowering_policy") is not None or canonical.get(
            "binder_lowering"
        ):
            if not canonical.get("instructions"):
                return EmitResult(
                    qasm="",
                    notes=[
                        "E_QPU_CANONICAL_FINITE_PROJECTION_UNAVAILABLE: "
                        "finite canonical projection produced no instructions"
                    ],
                    ok=False,
                    circuit=Circuit(
                        n_qubits=1,
                        n_bits=1,
                        reject_code="E_QPU_CANONICAL_FINITE_PROJECTION_UNAVAILABLE",
                    ),
                )
            fallback_note = (
                "W_QPU_FINITE_COMPAT_LOWERING: canonical finite policy is "
                "validated; instruction projection remains deferred"
            )
            logical = lower_unit_to_circuit(unit)
            notes = [fallback_note, *logical.notes]
            if logical.reject_code:
                return EmitResult(qasm="", notes=notes, ok=False, circuit=logical)
            circ = logical
            if self.route:
                topo = self._resolve_topo(logical.n_qubits)
                circ = route_circuit(logical, topo)
                notes.extend(circ.notes)
            return EmitResult(qasm=self.render(circ), notes=notes, ok=True, circuit=circ)
        diagnostics = qpu_ir_diagnostics(
            unit,
            canonical.get("canonical_semantic_ir"),
        )
        if diagnostics:
            first = diagnostics[0]
            return EmitResult(
                qasm="",
                notes=[str(first.get("message", first.get("code", "")))],
                ok=False,
                circuit=Circuit(
                    n_qubits=1,
                    n_bits=1,
                    reject_code=str(first.get("code", "E_QPU_UNSUPPORTED_CAPABILITY")),
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
            circuit=Circuit(
                n_qubits=1,
                n_bits=1,
                reject_code=code,
            ),
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
            return validation_error
        shape = program["hilbert_shape"]
        n_qubits = int(shape.get("logical_qubits", 0)) or 1
        resolved_values = dict(parameter_values or {})
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
                    circuit=Circuit(
                        n_qubits=n_qubits,
                        n_bits=1,
                        reject_code="E_QPU_UNSUPPORTED_CAPABILITY",
                    ),
                )
            angle = instruction.parameter if name in {"rx", "ry", "rz"} else None
            if isinstance(angle, str) and angle in resolved_values:
                angle = float(resolved_values[angle])
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
                    circuit=Circuit(
                        n_qubits=1,
                        n_bits=1,
                        reject_code="E_QPU_CANONICAL_PROVENANCE",
                    ),
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
                    circuit=Circuit(
                        n_qubits=1,
                        n_bits=1,
                        reject_code="E_QPU_CANONICAL_PROVENANCE",
                    ),
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
                    circuit=Circuit(
                        n_qubits=1,
                        n_bits=1,
                        reject_code="E_QPU_CANONICAL_PROVENANCE",
                    ),
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
                    circuit=Circuit(
                        n_qubits=1,
                        n_bits=1,
                        reject_code="E_QPU_CANONICAL_PROVENANCE",
                    ),
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
            circuit=Circuit(n_qubits=1, n_bits=1, reject_code=reject_code),
        )

    def _emit_from_qpu_ir_when_available(self, program: QpuProgram) -> EmitResult | None:
        if program.get("projection_error"):
            return self.emit_qpu_program(program)
        instructions = tuple(
            instruction
            for instruction in program.get("instructions", ())
            if instruction.opcode != "Measure"
        )
        if not instructions:
            return None
        return self.emit_qpu_program(program)

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
