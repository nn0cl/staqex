"""Shared runtime error types for extracted evaluator services."""

from __future__ import annotations

from typing import Any


class KernelError(Exception):
    """Base error raised while evaluating a Staqex kernel."""


class KernelDiagnosticError(KernelError, ValueError):
    """Runtime failure with a stable code and legacy ValueError compatibility."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        line: int = 0,
        col: int = 0,
        provenance: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.line = line
        self.col = col
        self.provenance = provenance
