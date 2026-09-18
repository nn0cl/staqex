"""Cohesive runtime evaluation services behind the public Evaluator facade."""

from .orchestration import dispatch_runtime_plan, execute_canonical_unit

__all__ = ["dispatch_runtime_plan", "execute_canonical_unit"]
