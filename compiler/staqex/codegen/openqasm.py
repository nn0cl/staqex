"""OpenQASM emit — ADR 0036 CLI path.

Prefer `compiler.staqex.codegen_qasm.OpenQASM3Generator` /
`StaqexCompiler.compile_to_qasm3` for the public AT-TDD API.
"""

from __future__ import annotations

from ..ast_nodes import CompilationUnit
from ..backend.qasm import EmitResult, emit_openqasm3 as _backend_emit
from ..scientific_semantic_ir import ScientificSemanticIR

__all__ = ["EmitResult", "emit_openqasm3"]


def emit_openqasm3(
    unit: CompilationUnit,
    *,
    semantic_ir: ScientificSemanticIR | None = None,
    topology: str = "linear",
    route: bool = True,
) -> EmitResult:
    return _backend_emit(
        unit,
        semantic_ir=semantic_ir,
        topology=topology,
        route=route,
    )
