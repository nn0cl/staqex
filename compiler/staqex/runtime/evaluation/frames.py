"""Invocation-frame successor boundary for the evaluator runtime.

The evaluator remains the live state owner.  These functions are deliberately
small compatibility entrypoints while the frame bodies are migrated in a
bounded follow-up slice.
"""

from __future__ import annotations

from typing import Any

from .context import EvaluatorContext


def bind_method(
    context: EvaluatorContext,
    joint: Any,
    name: str,
    receiver: Any,
    method: Any,
    args: list[Any],
    *,
    logs: list[str] | None = None,
    inspect_out: Any = None,
) -> Any:
    """Execute a method through the evaluator-owned frame implementation."""
    return context._legacy_bind_method(
        joint,
        name,
        receiver,
        method,
        args,
        logs=logs,
        inspect_out=inspect_out,
    )


def bind_user_function(
    context: EvaluatorContext,
    joint: Any,
    names: list[str],
    expr: Any,
    function: Any,
    *,
    logs: list[str] | None = None,
    inspect_out: Any = None,
) -> Any:
    """Execute a user function through the evaluator-owned frame implementation."""
    return context._legacy_bind_user_fun(
        joint,
        names,
        expr,
        function,
        logs=logs,
        inspect_out=inspect_out,
    )


def restore_frame(
    context: EvaluatorContext, receiver: Any, frame_units: dict[str, str]
) -> None:
    """Restore receiver and frame-unit state through explicit callbacks."""
    context._restore_frame(receiver, frame_units)
