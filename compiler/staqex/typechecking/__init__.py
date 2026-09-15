"""Incremental TypeChecker family boundaries."""

from .context import TypeCheckContext
from .declarations import check_declaration
from .dimensions import check_assignment
from .evolution import check_evolution
from .inference import infer_expression
from .operators import check_operator_expr

__all__ = [
    "TypeCheckContext",
    "check_assignment",
    "check_declaration",
    "check_evolution",
    "check_operator_expr",
    "infer_expression",
]
