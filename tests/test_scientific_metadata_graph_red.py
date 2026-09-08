"""Phase 1 Red tests for WP-0132 / LISS-0515 M0.

These tests intentionally target the not-yet-implemented Metadata Graph
contract.  They do not authorize or provide the implementation.  The graph
is descriptive evidence only; it must not become an execution authority.
"""

from __future__ import annotations

import importlib

import pytest


FIXTURES = (
    {"profile": "assay", "id": "assay:screen-01", "value_kind": "observed"},
    {"profile": "road-closure", "id": "road:closure-01", "value_kind": "observed"},
    {"profile": "astronomy-flux", "id": "ivoa:flux-01", "value_kind": "observed"},
    {"profile": "vector-field", "id": "field:velocity-01", "value_kind": "estimated"},
    {"profile": "physical-experiment", "id": "experiment:gravity-01", "value_kind": "observed"},
    {"profile": "discrete-interaction", "id": "graph:interaction-01", "value_kind": "observed"},
)


def _metadata_graph_module():
    """Load the M0 contract module once it exists."""

    try:
        return importlib.import_module("compiler.staqex.scientific_metadata")
    except ModuleNotFoundError as error:
        pytest.fail(
            "WP-0132 M0 requires compiler.staqex.scientific_metadata: "
            "Metadata Graph contract is not implemented yet"
        )
        raise AssertionError from error


def _graph():
    module = _metadata_graph_module()
    graph_type = getattr(module, "MetadataGraph")
    return graph_type.from_records(FIXTURES)


def test_m0_exposes_one_descriptive_graph_contract_for_all_six_fixtures() -> None:
    graph = _graph()

    assert set(graph.profiles()) == {fixture["profile"] for fixture in FIXTURES}
    assert graph.is_executable is False


def test_g01_snapshot_identity_is_order_independent_and_revision_is_immutable() -> None:
    module = _metadata_graph_module()
    graph_type = getattr(module, "MetadataGraph")
    first = graph_type.from_records(FIXTURES)
    reordered = graph_type.from_records(tuple(reversed(FIXTURES)))

    assert first.identity == reordered.identity
    with pytest.raises(module.ImmutableSnapshotError):
        first.records[0]["value_kind"] = "estimated"


@pytest.mark.parametrize(
    "invalid_record",
    [
        {"profile": "assay", "id": "assay:screen-01", "value_kind": "estimated"},
        {"profile": "assay", "id": "assay:bad-dimension", "unit": "m", "dimension": "Time"},
    ],
)
def test_g01_rejects_identity_and_dimension_conflicts(invalid_record: dict[str, str]) -> None:
    module = _metadata_graph_module()

    with pytest.raises(module.GraphValidationError):
        module.MetadataGraph.from_records((*FIXTURES, invalid_record))


def test_g01_rejects_a_dangling_relation_endpoint() -> None:
    module = _metadata_graph_module()

    with pytest.raises(module.GraphValidationError):
        module.MetadataGraph.from_records(
            FIXTURES,
            relations=(("assay:screen-01", "derived_from", "assay:no-such-id"),),
        )


def test_g02_preserves_zero_missing_interval_estimate_and_language_candidate() -> None:
    module = _metadata_graph_module()
    graph = module.MetadataGraph.from_records(
        (
            {"id": "obs:zero", "value": 0, "observation_kind": "observed"},
            {"id": "obs:not-measured", "value": None, "observation_kind": "not-measured"},
            {"id": "obs:below-limit", "value": "<0.1", "observation_kind": "below-detection"},
            {"id": "obs:estimate", "value": 0.2, "observation_kind": "model-estimate"},
            {"id": "obs:candidate", "value": "rain stopped", "observation_kind": "language-candidate"},
        )
    )

    assert graph.observation_kinds("obs:") == (
        "observed",
        "not-measured",
        "below-detection",
        "model-estimate",
        "language-candidate",
    )
    assert graph.value("obs:not-measured") is None
    assert graph.approval("obs:candidate") is None


def test_g03_tracks_supporting_refuting_evidence_and_correction_lineage() -> None:
    module = _metadata_graph_module()
    graph = module.MetadataGraph.from_records(
        (
            {"id": "result:r1", "kind": "result", "revision": 1},
            {"id": "result:r1", "kind": "result", "revision": 2},
            {"id": "evidence:support", "kind": "evidence", "polarity": "supporting"},
            {"id": "evidence:refute", "kind": "evidence", "polarity": "refuting"},
            {"id": "activity:a1", "kind": "activity"},
            {"id": "correction:r1", "kind": "correction", "derived_from": "result:r1@1"},
        ),
        relations=(
            ("result:r1", "supported_by", "evidence:support"),
            ("result:r1", "refuted_by", "evidence:refute"),
            ("result:r1", "generated_by", "activity:a1"),
        ),
    )

    assert graph.evidence_for("result:r1") == ("evidence:support", "evidence:refute")
    assert graph.correction_lineage("correction:r1") == ("result:r1@1", "result:r1@2")
    with pytest.raises(module.ProvenanceCycleError):
        module.MetadataGraph.from_records(
            (
                {"id": "activity:a1", "kind": "activity"},
                {"id": "activity:a2", "kind": "activity"},
            ),
            relations=(
                ("activity:a1", "derived_from", "activity:a2"),
                ("activity:a2", "derived_from", "activity:a1"),
            ),
        )


def test_m0_graph_has_no_execution_or_projection_authority() -> None:
    graph = _graph()

    assert not hasattr(graph, "execute")
    assert not hasattr(graph, "project_to_qpu")
    assert not hasattr(graph, "to_semantic_ir")
