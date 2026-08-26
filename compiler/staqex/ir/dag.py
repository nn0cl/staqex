"""Computation DAG IR — lower AST for deferred / accelerator backends (ADR 0032)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from ..ast_nodes import (
    Attr,
    BinOp,
    Call,
    Coin,
    CompilationUnit,
    Dirac,
    Expr,
    EvolveExpr,
    Inspect,
    Lambda,
    TupleExpr,
    LitBool,
    LitFloat,
    LitInt,
    LitString,
    Measure,
    Snapshot,
    StateBind,
    Vacuum,
    Var,
    WhenExpr,
)

OpKind = Literal[
    "input",
    "evolve",
    "coin",
    "dirac",
    "vacuum",
    "lit",
    "var",
    "binop",
    "when",
    "map",
    "project",
    "interfer",
    "phase",
    "diffuse",
    "cis",
    "math",
    "inspect",
    "bind",
    "snapshot",
    "measure",
]


@dataclass
class IrNode:
    id: int
    kind: OpKind
    attrs: dict[str, Any] = field(default_factory=dict)
    inputs: list[int] = field(default_factory=list)


@dataclass
class Dag:
    nodes: list[IrNode] = field(default_factory=list)
    binds: dict[str, int] = field(default_factory=dict)  # var → node id
    measure: int | None = None

    def add(self, kind: OpKind, *, attrs: dict[str, Any] | None = None, inputs: list[int] | None = None) -> int:
        nid = len(self.nodes)
        self.nodes.append(IrNode(id=nid, kind=kind, attrs=attrs or {}, inputs=list(inputs or [])))
        return nid

    def to_dot(self) -> str:
        lines = ["digraph StaqexDAG {", "  rankdir=LR;"]
        for n in self.nodes:
            label = f"{n.kind}\\n{n.attrs}" if n.attrs else n.kind
            label = label.replace('"', "'")
            lines.append(f'  n{n.id} [label="{label}"];')
            for src in n.inputs:
                lines.append(f"  n{src} -> n{n.id};")
        lines.append("}")
        return "\n".join(lines) + "\n"

    def summary(self) -> dict[str, Any]:
        return {
            "node_count": len(self.nodes),
            "kinds": [n.kind for n in self.nodes],
            "binds": dict(self.binds),
            "has_measure": self.measure is not None,
        }


_STATE_OPS = frozenset({"map", "project", "interfer", "phase", "diffuse", "grover_diffuse", "cis"})


class Lowerer:
    def __init__(self) -> None:
        self.dag = Dag()

    def lower_unit(self, unit: CompilationUnit) -> Dag:
        if unit.main is None:
            return self.dag
        for stmt in unit.main.body.stmts:
            if isinstance(stmt, StateBind):
                nid = self._lower_expr(stmt.expr)
                bid = self.dag.add("bind", attrs={"names": stmt.names}, inputs=[nid])
                for nm in stmt.names:
                    self.dag.binds[nm] = bid
            elif isinstance(stmt, Snapshot):
                nid = self._lower_expr(stmt.expr)
                self.dag.add("snapshot", attrs={"sink": stmt.sink}, inputs=[nid])
            elif isinstance(stmt, Measure):
                nid = self._lower_expr(stmt.expr)
                mid = self.dag.add("measure", attrs={"sink": stmt.sink}, inputs=[nid])
                self.dag.measure = mid
        return self.dag

    def _lower_expr(self, expr: Expr) -> int:
        if isinstance(expr, Coin):
            return self.dag.add("coin")
        if isinstance(expr, Vacuum):
            return self.dag.add("vacuum")
        if isinstance(expr, Dirac):
            a = self._lower_expr(expr.arg)
            return self.dag.add("dirac", inputs=[a])
        if isinstance(expr, (LitInt, LitFloat, LitBool, LitString)):
            return self.dag.add("lit", attrs={"value": getattr(expr, "value")})
        if isinstance(expr, Var):
            if expr.name in self.dag.binds:
                return self.dag.binds[expr.name]
            return self.dag.add("var", attrs={"name": expr.name})
        if isinstance(expr, BinOp):
            l = self._lower_expr(expr.lhs)
            r = self._lower_expr(expr.rhs)
            return self.dag.add("binop", attrs={"op": expr.op}, inputs=[l, r])
        if isinstance(expr, WhenExpr):
            c = self._lower_expr(expr.ctrl)
            arms = []
            inputs = [c]
            for arm in expr.arms:
                b = self._lower_expr(arm.body)
                inputs.append(b)
                arms.append({"pat": arm.pat, "else": arm.is_else, "body": b})
            return self.dag.add("when", attrs={"arms": arms}, inputs=inputs)
        if isinstance(expr, Inspect):
            inner = self._lower_expr(expr.expr)
            return self.dag.add("inspect", attrs={"label": expr.label}, inputs=[inner])
        if isinstance(expr, EvolveExpr):
            seeds = [self._lower_expr(s) for s in expr.seeds]
            inputs = list(seeds)
            if isinstance(expr.times, int):
                times_attr: Any = expr.times
            elif isinstance(expr.times, LitInt):
                times_attr = expr.times.value
            elif isinstance(expr.times, Var):
                times_attr = {"var": expr.times.name}
            else:
                times_attr = type(expr.times).__name__
            attrs: dict = {
                "times": times_attr,
                "explicit_transform": bool(expr.explicit_transform),
                "source_span": (expr.span.line, expr.span.col),
            }
            if expr.hamiltonian is not None:
                attrs["under"] = True
                inputs.append(self._lower_expr(expr.hamiltonian))
            if expr.duration is not None:
                inputs.append(self._lower_expr(expr.duration))
            if expr.body is not None:
                result_id = self._lower_expr(expr.body.result)
                inputs.append(result_id)
                if expr.explicit_transform:
                    attrs["application"] = "operator_state"
                    attrs["provenance"] = {
                        "source_span": (expr.body.result.span.line, expr.body.result.span.col),
                        "transform": result_id,
                        "generator": "written_in_operand",
                        "exponent": "written_in_propagator",
                        "propagator": (
                            result_id,
                            "lhs",
                        ),
                        "state": (result_id, "rhs"),
                    }
            return self.dag.add("evolve", attrs=attrs, inputs=inputs)
        if isinstance(expr, TupleExpr):
            items = [self._lower_expr(i) for i in expr.items]
            return self.dag.add("input", attrs={"tuple": len(items)}, inputs=items)
        if isinstance(expr, Call):
            return self._lower_call(expr)
        if isinstance(expr, Attr):
            obj = self._lower_expr(expr.obj)
            return self.dag.add("var", attrs={"attr": expr.name}, inputs=[obj])
        if isinstance(expr, Lambda):
            body = self._lower_expr(expr.body)
            return self.dag.add("map", attrs={"lambda": expr.param}, inputs=[body])
        from ..ast_nodes import KetLit

        if isinstance(expr, KetLit):
            return self.dag.add("dirac", attrs={"ket": expr.label})
        return self.dag.add("input", attrs={"note": type(expr).__name__})

    def _lower_call(self, expr: Call) -> int:
        callee = expr.callee
        arg_ids = [self._lower_expr(a) for a in expr.args]
        if isinstance(callee, Attr):
            if isinstance(callee.obj, Var) and callee.obj.name == "Math":
                return self.dag.add("math", attrs={"op": callee.name}, inputs=arg_ids)
            if isinstance(callee.obj, Var) and callee.obj.name == "Complex" and callee.name == "cis":
                return self.dag.add("cis", inputs=arg_ids)
            if callee.name in _STATE_OPS:
                obj = self._lower_expr(callee.obj)
                return self.dag.add(callee.name, inputs=[obj, *arg_ids])  # type: ignore[arg-type]
            obj = self._lower_expr(callee.obj)
            return self.dag.add("math", attrs={"op": callee.name, "ext": True}, inputs=[obj, *arg_ids])
        if isinstance(callee, Var):
            if callee.name in _STATE_OPS:
                return self.dag.add(callee.name, inputs=arg_ids)  # type: ignore[arg-type]
            if callee.name in {"sin", "cos", "exp", "sqrt", "abs", "log", "tan"}:
                return self.dag.add("math", attrs={"op": callee.name}, inputs=arg_ids)
            return self.dag.add("input", attrs={"call": callee.name}, inputs=arg_ids)
        return self.dag.add("input", attrs={"call": "?"}, inputs=arg_ids)


def lower_source_ast(unit: CompilationUnit) -> Dag:
    return Lowerer().lower_unit(unit)
