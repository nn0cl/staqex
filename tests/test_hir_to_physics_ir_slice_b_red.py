"""LISS-0115 Slice B acceptance tests for typed node extraction."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.hir import build_hir
from compiler.staqex.pipeline import compile_source


def _load_api():
    from compiler.staqex.physics_ir import (
        BinderNode,
        ChannelNode,
        OperatorAtom,
        build_physics_ir,
    )

    return BinderNode, ChannelNode, OperatorAtom, build_physics_ir


def _hir_for(source: str):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    assert compiled.unit is not None
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    return hir, compiled.unit


def test_operator_expression_extracts_typed_operator_atoms() -> None:
    _, _, OperatorAtom, build_physics_ir = _load_api()
    hir, unit = _hir_for(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X + Z
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    physics = build_physics_ir(hir, unit=unit)
    operator_nodes = [node for node in physics.nodes if node.kind == "Operator"]

    assert operator_nodes
    assert all(node.typed_reference is not None for node in operator_nodes)
    assert all(isinstance(atom, OperatorAtom) for atom in operator_nodes[0].atoms)


def test_binder_extraction_preserves_variables_domain_constraints_and_order() -> None:
    BinderNode, _, _, build_physics_ir = _load_api()
    hir, unit = _hir_for(
        """
        package t
        pub fn main() -> Unit {
            Operator H = sum (i in Index<4>) { Z[i] }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    physics = build_physics_ir(hir, unit=unit)
    binders = [node for node in physics.nodes if isinstance(node, BinderNode)]

    assert binders
    assert binders[0].variables == ("i",)
    assert binders[0].domain is not None
    assert binders[0].source_order >= 0
    assert not hasattr(binders[0], "expanded_terms")


def test_channel_extraction_preserves_domains_and_operands_without_execution() -> None:
    _, ChannelNode, _, build_physics_ir = _load_api()
    hir, unit = _hir_for(
        """
        package t
        pub fn main() -> Unit {
            Channel<Qubit, Qubit> noise = DepolarizingChannel(0.1)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    physics = build_physics_ir(hir, unit=unit)
    channels = [node for node in physics.nodes if isinstance(node, ChannelNode)]

    assert channels
    assert channels[0].input_domain is not None
    assert channels[0].output_domain is not None
    assert channels[0].operands
    assert not hasattr(channels[0], "execute")


if __name__ == "__main__":
    for test in (
        test_operator_expression_extracts_typed_operator_atoms,
        test_binder_extraction_preserves_variables_domain_constraints_and_order,
        test_channel_extraction_preserves_domains_and_operands_without_execution,
    ):
        test()
    print("OK — LISS-0115 Slice B")
