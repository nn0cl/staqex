"""AT-TDD Phase 1 Red: LISS-0479 residual semantic-family matrix.

This packet defines the observable matrix contract without implementing a
classifier or adding a new semantic authority.  The production boundary is
intentionally absent until the matrix and its negative cases receive a
separate Green approval.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


RESIDUAL_ROWS = (
    {
        "row_id": "ideal_limit",
        "source_id": "tests/fixtures/ideal_realization/ideal_limit.sqx",
        "family": "ideal-limit",
        "semantic_role": "ideal_or_symbolic",
        "finite_boundary": "explicit_realize",
        "status": "deferred",
        "code": None,
        "reason": "explicit_realize_required",
    },
    {
        "row_id": "observation",
        "source_id": "examples/basics/B16_effect_marking/effect_marking.sqx",
        "family": "observation",
        "semantic_role": "inspection_or_observation",
        "finite_boundary": "terminal_measurement_or_explicit_observation_contract",
        "status": "deferred",
        "code": None,
        "reason": "observation_contract_required",
    },
    {
        "row_id": "interference",
        "source_id": "tests/fixtures/semantic_meaning/interfer_phase_branch.sqx",
        "family": "interference",
        "semantic_role": "interference",
        "finite_boundary": "canonical_projection_only",
        "status": "rejected",
        "code": "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE",
        "reason": "interference_projection_not_authorized",
    },
)


def _classify(source: str, *, source_id: str):
    from compiler.staqex.residual_semantic_family_readiness import (
        classify_for_qpu,
    )

    return classify_for_qpu(source, source_id=source_id)


def test_every_residual_row_has_a_reachable_source_fixture() -> None:
    for row in RESIDUAL_ROWS:
        source_path = REPO / row["source_id"]
        assert source_path.is_file(), row["row_id"]
        assert source_path.read_text(encoding="utf-8").strip(), row["row_id"]


@pytest.mark.parametrize("row", RESIDUAL_ROWS, ids=lambda row: row["row_id"])
def test_each_residual_row_exposes_the_complete_disposition_contract(row) -> None:
    source = (REPO / row["source_id"]).read_text(encoding="utf-8")

    decision = _classify(source, source_id=row["source_id"])

    assert decision.row_id == row["row_id"]
    assert decision.family == row["family"]
    assert decision.semantic_role == row["semantic_role"]
    assert decision.finite_boundary == row["finite_boundary"]
    assert decision.status in {"ready", "rejected", "deferred"}
    assert decision.status == row["status"]
    assert decision.code == row["code"]
    assert decision.reason == row["reason"]
    assert decision.source_id == row["source_id"]


def test_deferred_or_rejected_rows_never_emit_an_artifact() -> None:
    for row in RESIDUAL_ROWS:
        if row["status"] == "ready":
            continue
        source = (REPO / row["source_id"]).read_text(encoding="utf-8")
        decision = _classify(source, source_id=row["source_id"])

        assert decision.artifact is None, row["row_id"]
        assert decision.qasm is None, row["row_id"]
        assert decision.provider_mapping is None, row["row_id"]


def test_matrix_does_not_reclassify_completed_measurement_families() -> None:
    source_id = "tests/fixtures/semantic_core/dynamic_measurement.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")

    decision = _classify(source, source_id=source_id)

    assert decision.family == "measurement"
    assert decision.semantic_role == "dynamic_measurement_feedback"
    assert decision.status == "rejected"


def test_unknown_residual_construct_fails_closed() -> None:
    with pytest.raises(ValueError, match="unsupported residual semantic family"):
        _classify(
            "unclassified residual construct",
            source_id="synthetic.unclassified-residual.sqx",
        )
