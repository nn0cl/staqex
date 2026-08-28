"""Offline conformance checks for the bounded dynamic OpenQASM subset."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping


@dataclass(frozen=True)
class DynamicQasmSubset:
    version: str
    gates: tuple[str, ...]
    supports_dynamic_measurement: bool
    supports_classical_conditions: bool
    supports_reset: bool
    supports_reuse: bool


@dataclass(frozen=True)
class DynamicQasmConformanceResult:
    status: str
    parse_ok: bool
    subset_version: str
    metadata: dict[str, object]
    measurement_mode: str
    outcome_dependencies: tuple[tuple[str, str, str], ...]
    wire_mapping: dict[str, str]
    branch_outcomes: tuple[tuple[str, str, str], ...]
    reset_wires: tuple[str, ...]
    reused_wires: tuple[str, ...]
    unsupported_branches: tuple[tuple[str, str], ...]
    diagnostic_codes: tuple[str, ...]
    qasm: str
    artifact: None
    allocation: None
    physical_execution_claimed: bool = False


_DECLARATION = re.compile(r"^(?:bit|qubit)(?:\[(\d+)\])?\s+([A-Za-z_]\w*)\s*;")
_MEASURE = re.compile(r"^([\w\[\]]+)\s*=\s*measure\s+([\w\[\]]+)\s*;")
_CONDITION = re.compile(r"^if\s*\(([^)]+)\)\s*\{")
_RESET = re.compile(r"^reset\s+([\w\[\]]+)\s*;")
_GATE = re.compile(r"^([A-Za-z_]\w*)\s+([\w\[\]]+)(?:\s*,\s*([\w\[\]]+))?\s*;")


def _append_diagnostic(diagnostics: list[str], code: str) -> None:
    if code not in diagnostics:
        diagnostics.append(code)


def _target_diagnostics(
    subset: DynamicQasmSubset,
    *,
    has_measurement: bool,
    has_conditions: bool,
    has_reset: bool,
    has_reuse: bool,
) -> tuple[str, ...]:
    missing = (
        (has_measurement and not subset.supports_dynamic_measurement)
        or (has_conditions and not subset.supports_classical_conditions)
        or (has_reset and not subset.supports_reset)
        or (has_reuse and not subset.supports_reuse)
    )
    return ("QASM_DYNAMIC_TARGET_UNSUPPORTED",) if missing else ()


def _result(
    *,
    status: str,
    subset: DynamicQasmSubset,
    metadata: Mapping[str, object],
    measurement_mode: str,
    outcome_dependencies: tuple[tuple[str, str, str], ...] = (),
    wire_mapping: dict[str, str] | None = None,
    branch_outcomes: tuple[tuple[str, str, str], ...] = (),
    reset_wires: tuple[str, ...] = (),
    reused_wires: tuple[str, ...] = (),
    unsupported_branches: tuple[tuple[str, str], ...] = (),
    diagnostics: tuple[str, ...] = (),
    qasm: str = "",
) -> DynamicQasmConformanceResult:
    return DynamicQasmConformanceResult(
        status=status,
        parse_ok=status == "accepted" or "QASM_DYNAMIC_TARGET_UNSUPPORTED" not in diagnostics,
        subset_version=subset.version,
        metadata=dict(metadata),
        measurement_mode=measurement_mode,
        outcome_dependencies=outcome_dependencies,
        wire_mapping=wire_mapping or {},
        branch_outcomes=branch_outcomes,
        reset_wires=reset_wires,
        reused_wires=reused_wires,
        unsupported_branches=unsupported_branches,
        diagnostic_codes=diagnostics,
        qasm=qasm,
        artifact=None,
        allocation=None,
    )


def validate_dynamic_qasm(
    qasm: str,
    *,
    subset: DynamicQasmSubset,
    metadata: Mapping[str, object],
) -> DynamicQasmConformanceResult:
    """Validate dynamic control without provider access or physical claims."""
    lines = [line.strip() for line in qasm.splitlines() if line.strip()]
    wire_mapping: dict[str, str] = {}
    measurements: dict[str, str] = {}
    reset_wires: list[str] = []
    reused_wires: list[str] = []
    outcome_dependencies: list[tuple[str, str, str]] = []
    branch_outcomes: list[tuple[str, str, str]] = []
    unsupported_branches: list[tuple[str, str]] = []
    diagnostics: list[str] = []
    condition_wire = ""
    condition_value = ""
    in_branch = False

    for line in lines:
        declaration = _DECLARATION.match(line)
        if declaration:
            wire_mapping[declaration.group(2)] = declaration.group(2)
            continue
        measurement = _MEASURE.match(line)
        if measurement:
            outcome, wire = measurement.groups()
            measurements[outcome] = wire
            continue
        condition = _CONDITION.match(line)
        if condition:
            expression = condition.group(1).strip()
            parts = re.match(r"([\w\[\]]+)\s*==\s*([01])$", expression)
            if parts:
                condition_wire, condition_value = parts.groups()
                outcome_dependencies.append((condition_wire, "if", expression))
                branch_outcomes.append((condition_wire, condition_value, "then"))
                in_branch = True
            else:
                _append_diagnostic(diagnostics, "QASM_DYNAMIC_CONDITION_INVALID")
            continue
        if line == "} else {" and condition_wire:
            branch_outcomes.append((condition_wire, "else", "else"))
            continue
        if line == "}":
            in_branch = False
            continue
        reset = _RESET.match(line)
        if reset:
            wire = reset.group(1)
            reset_wires.append(wire)
            if wire in reset_wires[:-1]:
                reused_wires.append(wire)
            continue
        gate = _GATE.match(line)
        if gate:
            name, first, second = gate.groups()
            if name not in subset.gates:
                if in_branch:
                    unsupported_branches.append((condition_wire, condition_value))
                else:
                    _append_diagnostic(diagnostics, "QASM_DYNAMIC_GATE_UNSUPPORTED")
            elif first in reset_wires and first not in reused_wires:
                reused_wires.append(first)
            if second and second in reset_wires and second not in reused_wires:
                reused_wires.append(second)
            continue

    for code in _target_diagnostics(
        subset,
        has_measurement=bool(measurements),
        has_conditions=bool(outcome_dependencies),
        has_reset=bool(reset_wires),
        has_reuse=bool(reused_wires),
    ):
        _append_diagnostic(diagnostics, code)
    if unsupported_branches:
        _append_diagnostic(diagnostics, "QASM_DYNAMIC_UNSUPPORTED_BRANCH")
    declared_reuse = metadata.get("reused_wires")
    if declared_reuse == () and reused_wires:
        _append_diagnostic(diagnostics, "QASM_DYNAMIC_REUSE_METADATA_REQUIRED")

    if diagnostics:
        return _result(
            status="rejected",
            subset=subset,
            metadata=metadata,
            measurement_mode="dynamic" if measurements else "none",
            outcome_dependencies=tuple(outcome_dependencies),
            wire_mapping=wire_mapping,
            branch_outcomes=tuple(branch_outcomes),
            reset_wires=tuple(reset_wires),
            reused_wires=tuple(reused_wires),
            unsupported_branches=tuple(unsupported_branches),
            diagnostics=tuple(diagnostics),
        )
    return _result(
        status="accepted",
        subset=subset,
        metadata=metadata,
        measurement_mode="dynamic" if measurements else "none",
        outcome_dependencies=tuple(outcome_dependencies),
        wire_mapping=wire_mapping,
        branch_outcomes=tuple(branch_outcomes),
        reset_wires=tuple(reset_wires),
        reused_wires=tuple(reused_wires),
        diagnostics=(),
        qasm=qasm,
    )
