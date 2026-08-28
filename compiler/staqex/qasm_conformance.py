"""Offline conformance checks for the supported static OpenQASM subset."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class StaticQasmSubset:
    version: str
    gates: tuple[str, ...]
    supports_terminal_measurement: bool
    supports_dynamic_control: bool


@dataclass(frozen=True, slots=True)
class QasmConformanceResult:
    status: str
    parse_ok: bool
    subset_version: str
    metadata: dict[str, Any]
    measurement_mode: str | None = None
    parameters: tuple[str, ...] = ()
    diagnostic_codes: tuple[str, ...] = ()
    qasm: str = ""
    artifact: None = None
    allocation: None = None
    physical_execution_claimed: bool = False


_HEADER = re.compile(r"^OPENQASM\s+3\.0;$")
_INCLUDE = re.compile(r'^include\s+"stdgates\.inc";$')
_QUBIT_DECL = re.compile(r"^qubit\[\d+\]\s+q;$")
_BIT_DECL = re.compile(r"^bit\[\d+\]\s+c;$")
_MEASURE = re.compile(r"^c\[\d+\]\s*=\s*measure\s+q\[\d+\];$")
_GATE = re.compile(r"^(?P<name>[a-z][a-z0-9]*)(?:\((?P<args>[^)]*)\))?\s+q\[\d+\](?:,\s*q\[\d+\])?;$")


def _result(
    *,
    status: str,
    parse_ok: bool,
    subset: StaticQasmSubset,
    metadata: Mapping[str, Any],
    diagnostics: tuple[str, ...] = (),
    qasm: str = "",
    measurement_mode: str | None = None,
    parameters: tuple[str, ...] = (),
) -> QasmConformanceResult:
    return QasmConformanceResult(
        status=status,
        parse_ok=parse_ok,
        subset_version=subset.version,
        metadata=dict(metadata),
        measurement_mode=measurement_mode,
        parameters=parameters,
        diagnostic_codes=diagnostics,
        qasm=qasm,
    )


def _reject(
    subset: StaticQasmSubset,
    metadata: Mapping[str, Any],
    code: str,
    *,
    parse_ok: bool,
) -> QasmConformanceResult:
    return _result(
        status="rejected",
        parse_ok=parse_ok,
        subset=subset,
        metadata=metadata,
        diagnostics=(code,),
    )


def _valid_static_prefix(lines: list[str]) -> bool:
    return (
        len(lines) >= 4
        and _HEADER.fullmatch(lines[0]) is not None
        and _INCLUDE.fullmatch(lines[1]) is not None
        and _QUBIT_DECL.fullmatch(lines[2]) is not None
        and _BIT_DECL.fullmatch(lines[3]) is not None
    )


def validate_static_qasm(
    qasm: str,
    *,
    subset: StaticQasmSubset,
    metadata: Mapping[str, Any],
) -> QasmConformanceResult:
    """Validate a static QASM document without invoking a simulator/provider."""

    lines = [line.strip() for line in qasm.splitlines() if line.strip()]
    if not _valid_static_prefix(lines):
        return _reject(
            subset, metadata, "QASM_STATIC_PARSE_ERROR", parse_ok=False
        )

    body = lines[4:]
    if any(line.startswith("if ") or line.startswith("while ") for line in body):
        return _reject(
            subset, metadata, "QASM_STATIC_DYNAMIC_UNSUPPORTED", parse_ok=True
        )

    measurements = [
        index for index, line in enumerate(body) if _MEASURE.fullmatch(line)
    ]
    if not measurements:
        return _reject(
            subset, metadata, "QASM_STATIC_EMPTY_PROGRAM", parse_ok=True
        )
    if not subset.supports_terminal_measurement or measurements != list(
        range(measurements[0], len(body))
    ):
        return _reject(
            subset, metadata, "QASM_STATIC_MEASUREMENT_UNSUPPORTED", parse_ok=True
        )

    parameters: list[str] = []
    for index, line in enumerate(body):
        if _MEASURE.fullmatch(line):
            continue
        gate = _GATE.fullmatch(line)
        if gate is None or gate.group("name") not in subset.gates:
            return _reject(
                subset, metadata, "QASM_STATIC_GATE_UNSUPPORTED", parse_ok=False
            )
        args = gate.group("args")
        if args:
            parameters.append(args.strip())

    return _result(
        status="accepted",
        parse_ok=True,
        subset=subset,
        metadata=metadata,
        qasm=qasm,
        measurement_mode="terminal",
        parameters=tuple(parameters),
    )
