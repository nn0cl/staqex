"""AT-TDD Phase 1 Red: LISS-0482 observation-to-semantic-IR mapping."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _map(source: str, *, source_id: str):
    from compiler.staqex.observation_semantic_mapping import map_source

    return map_source(source, source_id=source_id)


def test_mapping_fixture_is_reachable_and_source_owned() -> None:
    source_id = "tests/fixtures/observation_mapping/observation_operations.sqx"
    source_path = REPO / source_id

    assert source_path.is_file()
    result = _map(source_path.read_text(encoding="utf-8"), source_id=source_id)

    assert result.source_id == source_id
    assert result.semantic_authority == "scientific_semantic_ir"


def test_inspect_mapping_preserves_role_lane_and_provenance() -> None:
    source_id = "tests/fixtures/observation_mapping/observation_operations.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")
    result = _map(source, source_id=source_id)

    inspect = result.operations[0]
    assert inspect.kind == "inspect"
    assert inspect.semantic_role == "diagnostic_view"
    assert inspect.role_lane == "diagnostic"
    assert inspect.source_node_id
    assert inspect.provenance.source_id == source_id
    assert inspect.exactness == "preserved"
    assert inspect.dimensions == "preserved"
    assert inspect.projection_loss is None


def test_measure_mapping_is_terminal_and_collapsing() -> None:
    source_id = "tests/fixtures/observation_mapping/observation_operations.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")
    result = _map(source, source_id=source_id)

    measure = result.operations[1]
    assert measure.kind == "measure"
    assert measure.semantic_role == "terminal_measurement"
    assert measure.role_lane == "terminal_classical"
    assert measure.collapses is True
    assert measure.source_node_id
    assert measure.projection_loss is None


def test_mapping_never_creates_an_implicit_finite_artifact() -> None:
    source_id = "tests/fixtures/observation_mapping/observation_operations.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")
    result = _map(source, source_id=source_id)

    assert result.finite_artifact is None
    assert result.provider_payload is None
    assert result.projection_loss is None


def test_illegal_role_lane_transition_is_rejected_explicitly() -> None:
    with pytest.raises(ValueError, match="illegal observation role/lane transition"):
        _map(
            "measure as diagnostic",
            source_id="synthetic.observation.illegal-lane.sqx",
        )
