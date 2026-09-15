"""Capability and pre-allocation rejection decisions."""
from __future__ import annotations
from typing import Any
from . import legacy as _legacy

def qudit_capability_reject(unit: Any):
    return _legacy.qudit_capability_reject(unit)

def explicit_evolution_capability_reject(unit: Any, target_profile: Any = None):
    return _legacy.explicit_evolution_capability_reject(unit, target_profile)

def formal_limit_capability_reject(unit: Any, target_profile: Any = None):
    return _legacy.formal_limit_capability_reject(unit, target_profile)

def preflight(unit: Any, target_profile: Any = None):
    for check in (qudit_capability_reject, formal_limit_capability_reject, explicit_evolution_capability_reject):
        rejected = check(unit, target_profile) if check is not qudit_capability_reject else check(unit)
        if rejected is not None:
            return rejected
    return None

