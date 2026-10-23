"""Canonical semantic identity and serialization."""
from __future__ import annotations
from . import legacy as _legacy
from .model import ScientificSemanticIR

def semantic_fingerprint(core: ScientificSemanticIR) -> str:
    """Return the canonical digest without creating a second authority."""
    return _legacy.semantic_fingerprint(core)

