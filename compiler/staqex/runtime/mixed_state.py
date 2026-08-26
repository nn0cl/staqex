"""Runtime value and terminal measurement helpers for finite mixed states."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..ast_nodes import BinOp, Call, KetLit, ListExpr, LitFloat, LitInt, TupleExpr, Var
from .matrix import Matrix


@dataclass(frozen=True)
class DensityStateValue:
    matrix: Matrix
    domain: str
    operation: str


def density_from_call(
    expr: Call,
    *,
    domain: str,
    scalars: dict[str, float] | None = None,
    ket_labels: dict[str, str] | None = None,
) -> DensityStateValue:
    if len(expr.args) != 1 or not isinstance(expr.args[0], Call):
        raise ValueError("DensityState requires one Ensemble or RawMatrix input")
    source = expr.args[0]
    name = source.callee.name if isinstance(source.callee, Var) else ""
    if name == "RawMatrix":
        return DensityStateValue(
            matrix=matrix_from_list(source.args[0], scalars=scalars),
            domain=domain,
            operation="RawMatrix",
        )
    if name == "Ensemble":
        return DensityStateValue(
            matrix=_matrix_from_ensemble(
                source.args[0], scalars=scalars, ket_labels=ket_labels
            ),
            domain=domain,
            operation="Ensemble",
        )
    raise ValueError("DensityState input must be Ensemble or RawMatrix")


def matrix_from_list(expr: Any, *, scalars: dict[str, float] | None = None) -> Matrix:
    if not isinstance(expr, ListExpr):
        raise ValueError("RawMatrix requires a matrix list")
    rows: Matrix = []
    for row in expr.items:
        if not isinstance(row, ListExpr):
            raise ValueError("RawMatrix requires nested row lists")
        rows.append([complex(_number(value, scalars)) for value in row.items])
    return rows


def _matrix_from_ensemble(
    expr: Any,
    *,
    scalars: dict[str, float] | None = None,
    ket_labels: dict[str, str] | None = None,
) -> Matrix:
    if not isinstance(expr, ListExpr):
        raise ValueError("Ensemble requires a list")
    dimension = 2
    matrix: Matrix = [[0j for _ in range(dimension)] for _ in range(dimension)]
    for item in expr.items:
        if not isinstance(item, TupleExpr) or len(item.items) != 2:
            raise ValueError("Ensemble entries must be weighted states")
        weight = _number(item.items[0], scalars)
        state = item.items[1]
        label: str | None = None
        if isinstance(state, KetLit):
            label = state.label
        elif isinstance(state, Var) and ket_labels is not None:
            # LISS-0380: named State bound to |0>/|1> matches static Var allowlist.
            label = ket_labels.get(state.name)
        if label not in {"0", "1"}:
            raise ValueError("Ensemble MVP accepts |0> and |1>")
        index = int(label)
        matrix[index][index] += complex(weight)
    return matrix


def _number(expr: Any, scalars: dict[str, float] | None = None) -> float:
    """Resolve Ensemble/RawMatrix numeric leaves (LISS-0378)."""
    if isinstance(expr, LitInt):
        return float(expr.value)
    if isinstance(expr, LitFloat):
        return float(expr.value)
    if isinstance(expr, Var) and scalars is not None and expr.name in scalars:
        return float(scalars[expr.name])
    if isinstance(expr, BinOp):
        left = _number(expr.lhs, scalars)
        right = _number(expr.rhs, scalars)
        if expr.op == "+":
            return left + right
        if expr.op == "-":
            return left - right
        if expr.op == "*":
            return left * right
        if expr.op == "/":
            if right == 0.0:
                raise ValueError("mixed-state numeric input must be literal")
            return left / right
    raise ValueError("mixed-state numeric input must be literal")
