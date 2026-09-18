"""Shared runtime error types for extracted evaluator services."""

from __future__ import annotations


class KernelError(Exception):
    """Base error raised while evaluating a Staqex kernel."""

