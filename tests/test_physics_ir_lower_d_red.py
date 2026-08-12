"""LISS-0115 Slice D: compile_source / pipeline Physics IR wiring (Phase 1 Red)."""

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


def test_compile_source_exposes_physics_ir_module() -> None:
    from compiler.staqex.physics_ir import PhysicsModule

    compiled = compile_source(_operator_source())

    assert compiled.ok, compiled.diagnostics
    assert hasattr(compiled, "physics_ir")
    assert isinstance(compiled.physics_ir, PhysicsModule)
    assert compiled.physics_ir.nodes
    assert compiled.physics_ir.origins
    assert all(getattr(node, "origin", None) is not None for node in compiled.physics_ir.nodes)


def test_compile_source_physics_ir_matches_explicit_lower() -> None:
    from compiler.staqex.hir import build_hir
    from compiler.staqex.physics_ir_lower import lower_hir_to_physics_ir

    compiled = compile_source(_operator_source())
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    assert compiled.unit is not None

    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    explicit = lower_hir_to_physics_ir(hir, unit=compiled.unit)

    assert compiled.physics_ir is not None
    assert tuple(node.node_id for node in compiled.physics_ir.nodes) == tuple(
        node.node_id for node in explicit.nodes
    )
    assert compiled.physics_ir.origins == explicit.origins


def test_compile_source_physics_ir_diagnostics_are_non_hard() -> None:
    compiled = compile_source(_operator_source())

    assert compiled.ok, compiled.diagnostics
    assert compiled.physics_ir is not None
    physics_codes = {
        d.get("code")
        for d in compiled.diagnostics
        if isinstance(d.get("code"), str) and str(d.get("code")).startswith("PHYSICS_IR")
    }
    # Soft diagnostics may be absent or present; none may flip ok.
    assert compiled.ok is True
    assert all(code.startswith("PHYSICS_IR") for code in physics_codes)


def test_ordinary_program_still_compiles_without_requiring_equations() -> None:
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
    assert compiled.physics_ir is not None
    assert compiled.physics_ir.nodes or compiled.physics_ir.origins is not None


if __name__ == "__main__":
    for test in (
        test_compile_source_exposes_physics_ir_module,
        test_compile_source_physics_ir_matches_explicit_lower,
        test_compile_source_physics_ir_diagnostics_are_non_hard,
        test_ordinary_program_still_compiles_without_requiring_equations,
    ):
        test()
    print("OK — LISS-0115 Slice D")
