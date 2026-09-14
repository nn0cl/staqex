"""Cohesive runtime evaluation services behind the public Evaluator facade."""

from .plans import dispatch_runtime_plan

__all__ = ["dispatch_runtime_plan"]
