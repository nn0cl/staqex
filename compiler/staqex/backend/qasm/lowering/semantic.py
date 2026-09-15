"""Canonical semantic/QPU to circuit lowering boundary."""
from __future__ import annotations
from typing import Any
from . import legacy as _legacy
from ....scientific_semantic.model import ScientificSemanticIR

def lower_semantic_to_circuit(
    value: ScientificSemanticIR | Any, *args: Any, **kwargs: Any
):
    return _legacy._from_dag(value, *args, **kwargs)
