"""Runtime execution projection from canonical semantic nodes."""
from __future__ import annotations
from . import legacy as _legacy
from .model import RuntimeExecutionPlan, ScientificSemanticIR

def build_runtime_execution_plan(semantic_ir: ScientificSemanticIR) -> RuntimeExecutionPlan:
    return _legacy.build_runtime_execution_plan(semantic_ir)

