"""Provider-neutral, read-only Symbolic IR projection (LISS-0033)."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import Any

from .ast_nodes import (
    BinOp,
    Call,
    CompilationUnit,
    DiscretizationBridgeDecl,
    LitInt,
    OpBin,
    OpIndexed,
    OpLit,
    OpVar,
    StateBind,
    Var,
)
from .kernel_literals import SECOND_QUANTIZED_FAMILIES as _SECOND_QUANTIZED_FAMILIES


def _span(value: Any) -> dict[str, int] | None:
    source_span = getattr(value, "span", None)
    if source_span is None:
        return None
    return {"line": source_span.line, "col": source_span.col}


def _node(value: Any, node_id: str | None = None) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_node(item, f"{node_id}[{index}]") for index, item in enumerate(value)]
    if isinstance(value, tuple):
        return [_node(item, f"{node_id}[{index}]") for index, item in enumerate(value)]
    if is_dataclass(value):
        kind = type(value).__name__
        if kind.startswith("Op"):
            kind = kind[2:]
        result: dict[str, Any] = {"kind": kind}
        if node_id is not None:
            result["node_id"] = node_id
        for field in fields(value):
            name = field.name
            field_value = getattr(value, name)
            if name == "span":
                continue
            output_name = "binder_kind" if kind == "Binder" and name == "kind" else name
            child_id = f"{node_id}.{output_name}" if node_id is not None else None
            result[output_name] = _node(field_value, child_id)
        source_span = _span(value)
        if source_span is not None:
            result["source_span"] = source_span
        return result
    return repr(value)


def _atoms(expr: Any) -> list[dict[str, Any]]:
    if isinstance(expr, OpIndexed) and isinstance(expr.base, OpVar):
        if expr.base.name in {"create", "annihilate", "spin_raise", "spin_lower"}:
            index = int(expr.index.value) if isinstance(expr.index, OpLit) else None
            return [{"kind": expr.base.name, "index": index}]
        return []
    if isinstance(expr, OpBin) and expr.op == "*":
        return _atoms(expr.lhs) + _atoms(expr.rhs)
    if isinstance(expr, Call) and isinstance(expr.callee, Var):
        if expr.callee.name in {"create", "annihilate", "spin_raise", "spin_lower"}:
            index = None
            if expr.args and isinstance(expr.args[0], LitInt):
                index = expr.args[0].value
            return [{"kind": expr.callee.name, "index": index}]
        return []
    if isinstance(expr, BinOp) and expr.op == "*":
        return _atoms(expr.lhs) + _atoms(expr.rhs)
    return []


def _second_quantized_metadata(stmt: StateBind) -> dict[str, Any]:
    family = stmt.ty.name if stmt.ty is not None else "Operator"
    atoms = _atoms(stmt.expr)
    rank = {"create": 0, "spin_raise": 0, "annihilate": 1, "spin_lower": 1}
    ordered = sorted(atoms, key=lambda atom: (rank.get(atom["kind"], 9), atom["index"] is None, atom["index"]))
    inversions = sum(
        1
        for left in range(len(atoms))
        for right in range(left + 1, len(atoms))
        if (
            (rank.get(atoms[left]["kind"], 9), atoms[left]["index"])
            > (rank.get(atoms[right]["kind"], 9), atoms[right]["index"])
        )
    )
    statistics = {
        "FermionOperator": "fermionic",
        "BosonOperator": "bosonic",
        "SpinOperator": "spin",
        "QubitOperator": "qubit",
    }.get(family, "unknown")
    return {
        "statistics": statistics,
        "canonical_order": ordered,
        "exchange_sign": -1 if statistics == "fermionic" and inversions % 2 else 1,
    }


def _build_symbolic_ir_legacy(unit: CompilationUnit) -> dict[str, Any]:
    """Build the pre-canonical dictionary for compatibility only."""
    operators: dict[str, Any] = {}
    raw_exprs: dict[str, Any] = {}
    if unit.main is not None:
        for stmt in unit.main.body.stmts:
            if (
                isinstance(stmt, StateBind)
                and stmt.ty is not None
                and (stmt.ty.name == "Operator" or stmt.ty.name in _SECOND_QUANTIZED_FAMILIES)
                and len(stmt.names) == 1
            ):
                operator = _node(
                    stmt.expr, f"operator:{stmt.names[0]}"
                )
                if stmt.ty.name in _SECOND_QUANTIZED_FAMILIES:
                    operator["second_quantized"] = _second_quantized_metadata(stmt)
                operators[stmt.names[0]] = operator
                raw_exprs[stmt.names[0]] = stmt.expr
    mappings: list[dict[str, Any]] = []
    for name, operator in operators.items():
        callee = operator.get("callee", {})
        if operator.get("kind") == "Call" and callee.get("name") == "map":
            args = operator.get("args", [])
            mapping_name = args[1].get("name") if len(args) > 1 else None
            operand_name = args[0].get("name") if args else None
            source_expr = raw_exprs.get(operand_name) if operand_name else None
            source_atoms = _atoms(source_expr) if source_expr is not None else []
            indices = [a["index"] for a in source_atoms if a["index"] is not None]
            qubit_count = max(indices) + 1 if indices else 0
            mappings.append(
                {"operator": name, "mapping": mapping_name, "qubit_count": qubit_count}
            )
    operator_ids = [f"operator:{name}" for name in operators]
    discretizations = [
        {
            "alias": declaration.alias,
            "contract": declaration.contract,
            "source": declaration.source,
        }
        for declaration in unit.decls
        if isinstance(declaration, DiscretizationBridgeDecl)
    ]
    return {
        "kind": "SymbolicProgram",
        "operators": operators,
        "provenance": [
            {
                "pass": "source",
                "input": "CompilationUnit",
                    "output": "SymbolicProgram",
                    "output_node_ids": operator_ids,
                    "source_span": _span(unit.main) if unit.main is not None else None,
                    "metadata": {"approximation": None, "mapping": None},
                }
            ],
        "resolved": {
            "kind": "ResolvedProgram",
            "source_node_ids": operator_ids,
            "status": "unresolved",
            "approximations": [],
            "mappings": mappings,
            "discretizations": discretizations,
        },
    }


def build_symbolic_ir(unit: CompilationUnit) -> dict[str, Any]:
    """Compatibility API for callers that explicitly request the legacy view."""

    return _build_symbolic_ir_legacy(unit)


def build_symbolic_compatibility_view(
    semantic_ir: Any,
    unit: CompilationUnit,
) -> dict[str, Any]:
    """Attach canonical identity to the legacy-shaped inspection view."""

    view = _build_symbolic_ir_legacy(unit)
    canonical_source_node_ids = [node.node_id for node in semantic_ir.nodes]
    view["authority"] = {
        "semantic_authority": semantic_ir.authority,
        "semantic_fingerprint": _semantic_fingerprint(semantic_ir),
        "role": "derived_inspection_compatibility",
    }
    view["resolved"]["canonical_source_node_ids"] = canonical_source_node_ids
    view["canonical_nodes"] = [
        {
            "node_id": node.node_id,
            "kind": node.kind,
            "children": list(node.children),
            "role_lane": node.role_lane,
            "type": node.type,
            "dimensions": node.dimensions,
            "exactness": node.exactness,
            "intent": node.intent,
            "source_span": {
                "line": node.provenance.line,
                "col": node.provenance.col,
            },
        }
        for node in semantic_ir.nodes
    ]
    return view


def _semantic_fingerprint(semantic_ir: Any) -> str:
    """Avoid making the legacy compatibility module a semantic dependency."""

    from .scientific_semantic_ir import semantic_fingerprint

    return semantic_fingerprint(semantic_ir)
