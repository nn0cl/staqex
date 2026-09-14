"""Evolution-family entrypoint during the incremental evaluator extraction."""

from __future__ import annotations

from typing import Any

from .context import EvaluatorContext


def execute_evolution(
    context: EvaluatorContext, joint: Any, names: list[str], expr: Any
) -> Any:
    """Delegate evolution while preserving ordering and mutable state ownership."""
    return context._legacy_hamiltonian_evolve_one_step(joint, names, expr)
