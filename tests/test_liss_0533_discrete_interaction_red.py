"""Phase 1 Red contracts for LISS-0533 R01."""

from __future__ import annotations

import importlib

import pytest


def _profile_module():
    try:
        return importlib.import_module("compiler.staqex.discrete_interaction_profile")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0533 R01 interaction profile is not present yet")
        raise AssertionError from error


def _graph(module):
    return module.InteractionGraph(
        graph_id="graph:r01-spin-chain-3-v1",
        nodes=("spin:0", "spin:1", "spin:2"),
        edges=(
            module.InteractionEdge("edge:01", "spin:0", "spin:1", 1.0),
            module.InteractionEdge("edge:12", "spin:1", "spin:2", -0.5),
        ),
        source_hash="sha256:r01-source-v1",
    )


def _law(module):
    return module.InteractionLaw(
        law_id="ising:r01-v1",
        local_fields={"spin:0": 0.25, "spin:1": 0.0, "spin:2": -0.25},
        weight_unit="dimensionless",
        symmetry="undirected",
    )


def test_r01_projects_explicit_graph_and_law_with_energy_decode_round_trip() -> None:
    module = _profile_module()

    projection = module.project_interaction(
        graph=_graph(module),
        law=_law(module),
        target="finite-binary-projection",
    )

    assert projection.kind == "ising-hamiltonian"
    assert projection.variable_index == {
        "spin:0": 0,
        "spin:1": 1,
        "spin:2": 2,
    }
    assert projection.energy((1, 1, 1)) == pytest.approx(0.5, abs=1e-12)
    assert projection.decode((1, -1, 1)) == {
        "spin:0": 1,
        "spin:1": -1,
        "spin:2": 1,
    }


def test_r01_rejects_graph_as_hamiltonian_without_explicit_interaction_law() -> None:
    module = _profile_module()

    with pytest.raises(module.DiscreteProfileError, match="Hamiltonian"):
        module.project_interaction(
            graph=_graph(module),
            law=None,
            target="finite-binary-projection",
        )


def test_r01_rejects_duplicate_edge_before_projection() -> None:
    module = _profile_module()
    graph = _graph(module)
    duplicate = module.InteractionGraph(
        graph_id=graph.graph_id,
        nodes=graph.nodes,
        edges=graph.edges + (module.InteractionEdge("edge:01-copy", "spin:1", "spin:0", 1.0),),
        source_hash=graph.source_hash,
    )

    with pytest.raises(module.DiscreteProfileError, match="duplicate edge"):
        module.project_interaction(
            graph=duplicate,
            law=_law(module),
            target="finite-binary-projection",
        )


def test_r01_rejects_index_map_that_does_not_cover_graph_nodes() -> None:
    module = _profile_module()
    law = _law(module)
    mismatched = module.InteractionLaw(
        law_id=law.law_id,
        local_fields={"spin:0": 0.25, "spin:1": 0.0, "spin:x": -0.25},
        weight_unit=law.weight_unit,
        symmetry=law.symmetry,
    )

    with pytest.raises(module.DiscreteProfileError, match="index"):
        module.project_interaction(
            graph=_graph(module),
            law=mismatched,
            target="finite-binary-projection",
        )


def test_r01_rejects_unsupported_projection_target_without_partial_result() -> None:
    module = _profile_module()

    with pytest.raises(module.DiscreteProfileError, match="unsupported target"):
        module.project_interaction(
            graph=_graph(module),
            law=_law(module),
            target="generic-live-qpu",
        )
