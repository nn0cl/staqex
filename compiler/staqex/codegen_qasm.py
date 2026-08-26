"""OpenQASM 3.0 codegen facade (Python standard library only).

Public API requested by AT-TDD:
  - `OpenQASM3Generator` — typed AST / CompilationUnit → OpenQASM 3.0 text
  - `StaqexCompiler.compile_to_qasm3(path)` — file → QASM string

Lowering reuses the existing Phase 4.1 QPU backend (`backend.qasm`) so SV-10/11
and CLI `emit-qasm` stay consistent. No third-party quantum SDKs are imported.
"""

from __future__ import annotations

from pathlib import Path

from .ast_nodes import CompilationUnit
from .backend.qasm import EmitResult, QASM3Emitter, emit_openqasm3
from .finite_binder import identity_acting_space_diagnostics
from .pipeline import compile_path, compile_source
from .resource_profile import ResourceProfile, SimulationResourceEstimate
from .scientific_semantic_ir import ScientificSemanticIR


class OpenQASM3Generator:
    """Convert a type-checked Staqex compilation unit into OpenQASM 3.0 text."""

    def __init__(self, *, topology: str = "linear", route: bool = True) -> None:
        self.topology = topology
        self.route = route

    def generate(
        self,
        unit: CompilationUnit,
        *,
        semantic_ir: ScientificSemanticIR | None = None,
        resource_profile: ResourceProfile | None = None,
        resource_estimate: SimulationResourceEstimate | None = None,
    ) -> str:
        """Emit OpenQASM 3.0 for `unit` (header, registers, gates, measure)."""
        result = self.generate_detailed(
            unit,
            semantic_ir=semantic_ir,
            resource_profile=resource_profile,
            resource_estimate=resource_estimate,
        )
        if not result.ok:
            code = result.circuit.reject_code if result.circuit else None
            detail = "; ".join(result.notes) if result.notes else "unknown"
            raise RuntimeError(
                f"OpenQASM 3 emission failed"
                + (f" [{code}]" if code else "")
                + f": {detail}"
            )
        text = result.qasm
        return text if text.endswith("\n") else text + "\n"

    def generate_detailed(
        self,
        unit: CompilationUnit,
        *,
        semantic_ir: ScientificSemanticIR | None = None,
        resource_profile: ResourceProfile | None = None,
        resource_estimate: SimulationResourceEstimate | None = None,
    ) -> EmitResult:
        return QASM3Emitter(topology=self.topology, route=self.route).emit_unit(
            unit,
            semantic_ir=semantic_ir,
            resource_profile=resource_profile,
            resource_estimate=resource_estimate,
        )

    def generate_from_source(self, source: str) -> str:
        compiled = compile_source(source)
        compiled.diagnostics.extend(
            identity_acting_space_diagnostics(compiled.unit) if compiled.unit else []
        )
        if not compiled.ok or compiled.unit is None:
            codes = [d.get("code") for d in compiled.diagnostics]
            raise ValueError(f"Staqex compile failed before QASM emit: {codes}")
        return self.generate(compiled.unit, semantic_ir=compiled.scientific_semantic_ir)


class StaqexCompiler:
    """Thin compiler entry for path-based QASM export."""

    def __init__(self, *, topology: str = "linear", route: bool = True) -> None:
        self._gen = OpenQASM3Generator(topology=topology, route=route)

    def compile_to_qasm3(self, file_path: str) -> str:
        """Compile `file_path` (typecheck + lower) to an OpenQASM 3.0 string."""
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Staqex source not found: {file_path}")
        compiled = compile_path(path)
        compiled.diagnostics.extend(
            identity_acting_space_diagnostics(compiled.unit) if compiled.unit else []
        )
        if not compiled.ok or compiled.unit is None:
            codes = [d.get("code") for d in compiled.diagnostics]
            raise ValueError(
                f"Staqex compile failed for `{file_path}` before QASM emit: {codes}"
            )
        return self._gen.generate(
            compiled.unit, semantic_ir=compiled.scientific_semantic_ir
        )


def generate_openqasm3(
    unit: CompilationUnit,
    *,
    semantic_ir: ScientificSemanticIR | None = None,
    **kwargs,
) -> str:
    """Convenience wrapper used by CLI / tests."""
    return OpenQASM3Generator(**kwargs).generate(unit, semantic_ir=semantic_ir)


__all__ = [
    "EmitResult",
    "OpenQASM3Generator",
    "StaqexCompiler",
    "emit_openqasm3",
    "generate_openqasm3",
]
