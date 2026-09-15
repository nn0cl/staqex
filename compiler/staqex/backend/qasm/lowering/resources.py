"""Allocation and budget verification."""
from __future__ import annotations
from typing import Any
from . import legacy as _legacy

def register_resource_budget_reject(unit: Any, target_profile: Any = None):
    return _legacy.register_resource_budget_reject(unit, target_profile)

