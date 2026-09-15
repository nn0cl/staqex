"""Source-derived canonical IR construction and read-only views."""
from __future__ import annotations
from typing import Any
from . import legacy as _legacy
from .model import ScientificSemanticIR, SemanticInspectionResult, SemanticRejection

def build_scientific_semantic_ir(
    unit: Any, *args: Any, **kwargs: Any
) -> ScientificSemanticIR:
    return _legacy.build_scientific_semantic_ir(unit, *args, **kwargs)

def build_inspection(core: ScientificSemanticIR) -> SemanticInspectionResult:
    return _legacy.build_inspection(core)

def build_rejection(core: ScientificSemanticIR, diagnostics: list[dict[str, Any]]) -> SemanticRejection | None:
    return _legacy.build_rejection(core, diagnostics)
