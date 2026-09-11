"""Phase 1 Red tests for WP-0136 / LISS-0519 D03."""

from __future__ import annotations

import importlib

import pytest


def _batch_module():
    try:
        return importlib.import_module("compiler.staqex.s02_classical_batch_baseline")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0519 D03 implementation is not present yet")
        raise AssertionError from error


def _candidates() -> tuple[dict[str, object], ...]:
    return (
        {"candidate_id": "candidate:001", "predicted_ic50_nM": 1.0, "cost": 3, "stock": True, "diversity_group": "group:A"},
        {"candidate_id": "candidate:002", "predicted_ic50_nM": 2.0, "cost": 3, "stock": True, "diversity_group": "group:B"},
        {"candidate_id": "candidate:003", "predicted_ic50_nM": 3.0, "cost": 2, "stock": True, "diversity_group": "group:A"},
        {"candidate_id": "candidate:004", "predicted_ic50_nM": 4.0, "cost": 2, "stock": True, "diversity_group": "group:C"},
        {"candidate_id": "candidate:005", "predicted_ic50_nM": 5.0, "cost": 1, "stock": True, "diversity_group": "group:D"},
    )


def _profile(module, *, budget: int = 8):
    return module.BatchProfile(
        profile_id="batch:s02-v1",
        candidate_set_id="candidates:s02-fixture-v1",
        batch_size=2,
        budget=budget,
        max_per_diversity_group=1,
        objective="minimize_predicted_ic50_nM",
    )


def test_d03_oracle_and_baseline_use_same_candidates_constraints_and_score() -> None:
    module = _batch_module()
    candidates = _candidates()
    profile = _profile(module)

    oracle = module.enumerate_batches(candidates, profile)
    baseline = module.greedy_baseline(candidates, profile)
    comparison = module.compare_selections(oracle, baseline)

    assert oracle.status == "accepted"
    assert oracle.feasible is True
    assert baseline.status == "accepted"
    assert comparison.status == "matched"
    assert oracle.selected_candidate_ids == baseline.selected_candidate_ids == (
        "candidate:001",
        "candidate:002",
    )
    assert oracle.score == baseline.score == 3.0


def test_d03_returns_no_feasible_plan_instead_of_empty_success() -> None:
    module = _batch_module()
    oracle = module.enumerate_batches(_candidates(), _profile(module, budget=1))

    assert oracle.status == "no-feasible-plan"
    assert oracle.feasible is False
    assert oracle.selected_candidate_ids == ()
    assert oracle.diagnostic.code == "BATCH_NO_FEASIBLE_PLAN"


def test_d03_rejects_candidate_set_mismatch_between_oracle_and_baseline() -> None:
    module = _batch_module()
    profile = _profile(module)
    oracle = module.enumerate_batches(_candidates(), profile)
    baseline = module.greedy_baseline(_candidates()[:-1], profile)

    comparison = module.compare_selections(oracle, baseline)

    assert comparison.status == "quarantine"
    assert comparison.diagnostic.code == "BATCH_CANDIDATE_SET_MISMATCH"


def test_d03_rejects_constraint_or_score_mismatch_as_non_comparable() -> None:
    module = _batch_module()
    profile = _profile(module)
    oracle = module.enumerate_batches(_candidates(), profile)
    altered = module.SelectionResult(
        status="accepted",
        method="greedy-feasible-v1",
        candidate_set_id=oracle.candidate_set_id,
        feasible=True,
        selected_candidate_ids=("candidate:003", "candidate:004"),
        score=7.0,
        diagnostic=None,
    )

    comparison = module.compare_selections(oracle, altered)

    assert comparison.status == "quarantine"
    assert comparison.diagnostic.code in {
        "BATCH_CONSTRAINT_MISMATCH",
        "BATCH_SCORE_MISMATCH",
    }
