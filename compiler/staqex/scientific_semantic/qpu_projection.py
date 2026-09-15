"""Finite QPU projection and rejection evidence boundary."""
from __future__ import annotations
from typing import Any
from . import legacy as _legacy
from .model import CanonicalQpuProjection, ScientificSemanticIR

def build_qpu_projection(unit: Any, core: ScientificSemanticIR) -> CanonicalQpuProjection:
    return _legacy._build_qpu_projection(unit, core)

def build_lowering_policy(unit: Any, core: ScientificSemanticIR) -> dict[str, Any] | None:
    return _legacy._build_lowering_policy(unit, core)

def build_explicit_evolution(unit: Any, core: ScientificSemanticIR) -> dict[str, Any] | None:
    return _legacy._build_explicit_evolution(unit, core)

