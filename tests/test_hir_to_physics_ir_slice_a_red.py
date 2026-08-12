"""LISS-0115 Slice A acceptance tests for the HIR-to-Physics IR root."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.hir import build_hir
from compiler.staqex.pipeline import compile_source


def _load_api():
    from compiler.staqex.physics_ir import PhysicsModule, build_physics_ir

    return PhysicsModule, build_physics_ir


def _hir_fixture():
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X + Z
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    return compiled, hir


def test_hir_to_physics_ir_builder_is_importable() -> None:
    PhysicsModule, build_physics_ir = _load_api()

    assert PhysicsModule is not None
    assert callable(build_physics_ir)


def test_hir_lowers_to_immutable_physics_module_with_provenance() -> None:
    PhysicsModule, build_physics_ir = _load_api()
    compiled, hir = _hir_fixture()

    physics = build_physics_ir(hir, unit=compiled.unit)

    assert isinstance(physics, PhysicsModule)
    assert physics.origins
    assert physics.nodes
    assert all(getattr(node, "origin", None) is not None for node in physics.nodes)
    try:
        physics.nodes = ()  # type: ignore[misc]
        mutated = True
    except (AttributeError, TypeError):
        mutated = False
    assert mutated is False


def test_same_hir_produces_stable_physics_node_identity() -> None:
    _, build_physics_ir = _load_api()
    compiled, hir = _hir_fixture()

    first = build_physics_ir(hir, unit=compiled.unit)
    second = build_physics_ir(hir, unit=compiled.unit)

    assert tuple(node.node_id for node in first.nodes) == tuple(
        node.node_id for node in second.nodes
    )
    assert first.origins == second.origins


def test_hir_to_physics_ir_does_not_rewire_evaluator() -> None:
    _, build_physics_ir = _load_api()
    compiled, hir = _hir_fixture()

    physics = build_physics_ir(hir, unit=compiled.unit)

    # Explicit builder remains a separate callable. Slice D may soft-attach
    # CompileResult.physics_ir without hard-failing compile or replacing the
    # evaluator entry path.
    assert physics is not None
    assert compiled.ok
    assert physics is not compiled.physics_ir


if __name__ == "__main__":
    for test in (
        test_hir_to_physics_ir_builder_is_importable,
        test_hir_lowers_to_immutable_physics_module_with_provenance,
        test_same_hir_produces_stable_physics_node_identity,
        test_hir_to_physics_ir_does_not_rewire_evaluator,
    ):
        test()
    print("OK — LISS-0115 Slice A")
