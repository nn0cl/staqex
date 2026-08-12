"""LISS-0082 Slice F: soft CompileResult.quantum_semantic_ir wire (Phase 1 Red)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _operator_source() -> str:
    return """
    package t
    pub fn main() -> Unit {
        Operator H = X + Z
        State<Int> observed = Coin()
        Measure observed
    }
    """


def test_compile_source_exposes_quantum_semantic_ir_module() -> None:
    from compiler.staqex.quantum_semantic_ir import QuantumSemanticModule

    compiled = compile_source(_operator_source())

    assert compiled.ok, compiled.diagnostics
    assert hasattr(compiled, "quantum_semantic_ir")
    assert isinstance(compiled.quantum_semantic_ir, QuantumSemanticModule)
    assert compiled.quantum_semantic_ir.schema_version == 1


def test_compile_source_quantum_semantic_ir_matches_explicit_soft_lower() -> None:
    from compiler.staqex.quantum_semantic_ir import (
        QuantumSemanticInput,
        lower_physics_to_quantum_semantic_ir,
    )

    compiled = compile_source(_operator_source())
    assert compiled.ok, compiled.diagnostics
    assert compiled.physics_ir is not None

    explicit = lower_physics_to_quantum_semantic_ir(
        QuantumSemanticInput(
            physics_module=compiled.physics_ir,
            finite_carrier_evidence=(),
            linear_resource_evidence=(),
            lane="StaticKernel",
            exactness=(),
        )
    )

    assert compiled.quantum_semantic_ir is not None
    assert compiled.quantum_semantic_ir.schema_version == explicit.module.schema_version
    assert compiled.quantum_semantic_ir.origins == explicit.module.origins
    assert compiled.quantum_semantic_ir is not explicit.module


def test_compile_source_qsem_diagnostics_are_non_hard() -> None:
    compiled = compile_source(_operator_source())

    assert compiled.ok, compiled.diagnostics
    assert compiled.quantum_semantic_ir is not None
    qsem_codes = {
        d.get("code")
        for d in compiled.diagnostics
        if isinstance(d.get("code"), str) and str(d.get("code")).startswith("QSEM_")
    }
    assert compiled.ok is True
    assert all(str(code).startswith("QSEM_") for code in qsem_codes)


def test_ordinary_program_still_compiles_with_soft_semantic_ir() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.quantum_semantic_ir is not None
    assert compiled.quantum_semantic_ir.schema_version == 1


if __name__ == "__main__":
    for test in (
        test_compile_source_exposes_quantum_semantic_ir_module,
        test_compile_source_quantum_semantic_ir_matches_explicit_soft_lower,
        test_compile_source_qsem_diagnostics_are_non_hard,
        test_ordinary_program_still_compiles_with_soft_semantic_ir,
    ):
        test()
    print("OK — LISS-0082 Slice F")
