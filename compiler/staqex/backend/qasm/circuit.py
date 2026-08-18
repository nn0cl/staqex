"""Logical → physical gate IR for OpenQASM emission."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

GateName = Literal[
    "h", "x", "y", "z", "s", "t", "rx", "ry", "rz", "cx", "cz", "swap", "measure"
]


@dataclass
class Gate:
    name: GateName
    qubits: tuple[int, ...]  # logical indices before routing; physical after
    bits: tuple[int, ...] = ()
    angle: float | str | None = None  # radians or symbolic parameter for rx/ry/rz
    comment: str = ""


@dataclass
class Circuit:
    n_qubits: int
    n_bits: int
    gates: list[Gate] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    # Set when lowering cannot produce a faithful gate circuit (LISS-0008).
    reject_code: str | None = None
    # Typed target-boundary evidence.  Rejections carry this envelope even
    # when no circuit allocation has started.
    provenance: dict[str, object] | None = None
    allocation_started: bool = False
    allocated_qubits: tuple[int, ...] = ()
    partial_program: object | None = None

    def add(self, gate: Gate) -> None:
        self.gates.append(gate)
