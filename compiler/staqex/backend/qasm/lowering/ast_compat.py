"""Diagnostic-only bounded AST compatibility path."""
from __future__ import annotations
from typing import Any
from . import legacy as _legacy

def lower_ast_compat(unit: Any, *args: Any, **kwargs: Any):
    return _legacy._from_ast_patterns(unit, *args, **kwargs)

