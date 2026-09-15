"""Explicit finite realization and algorithm-plan records."""
from __future__ import annotations
from typing import Any
from . import legacy as _legacy
from .model import FiniteRealizationRecord, ScientificSemanticIR

def build_algorithm_plan(core: ScientificSemanticIR) -> Any:
    return _legacy.build_algorithm_plan(core)

def build_finite_realization_record(unit: Any, core: ScientificSemanticIR) -> tuple[str | None, FiniteRealizationRecord | None, tuple[str, ...]]:
    return _legacy._build_finite_realization_record(unit, core)

