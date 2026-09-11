"""Phase 1 Red tests for WP-0151 / LISS-0534 Unit B."""

from __future__ import annotations

import importlib

import pytest


def _evidence_module():
    try:
        return importlib.import_module("compiler.staqex.reproducibility_evidence")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0534 Unit B implementation is not present yet")
        raise AssertionError from error


def _manifest(module):
    return module.RunManifest(
        manifest_id="manifest:s02-d03-v1",
        source_hash="sha256:source-001",
        fixture_hash="sha256:fixture-001",
        input_snapshot_id="snapshot:s02-round-001",
        model_revision="model:s02-v1",
        baseline_revision="baseline:greedy-feasible-v1",
        seed=17,
        numeric_precision="f64",
        runtime_version="python:3.14",
        command="s02-d03-replay",
    )


def _claim(module, **overrides):
    values = {
        "manifest": _manifest(module),
        "run_ids": ("run:001", "run:002"),
        "training_ids": ("compound:001", "compound:002"),
        "heldout_ids": ("compound:003",),
        "evaluated_run_ids": ("run:001", "run:002"),
        "metric_name": "mae",
        "metric_value": 0.2,
        "metric_threshold": 0.5,
        "cost": module.CostBreakdown(queue=1.0, encode=2.0, execute=3.0, decode=1.0),
        "prospective_available": True,
    }
    values.update(overrides)
    return module.ClaimInput(**values)


def test_unit_b_reports_reproduced_only_for_complete_predeclared_evaluation() -> None:
    module = _evidence_module()

    result = module.evaluate_claim(_claim(module))

    assert result.claim == "reproduced"


def test_unit_b_rejects_heldout_reuse_before_claiming_success() -> None:
    module = _evidence_module()

    result = module.evaluate_claim(
        _claim(module, training_ids=("compound:001", "compound:003"))
    )

    assert result.claim == "not-evaluated"
    assert result.diagnostic.code == "EVIDENCE_HELDOUT_REUSE"


def test_unit_b_rejects_a_run_subset_as_a_biased_denominator() -> None:
    module = _evidence_module()

    result = module.evaluate_claim(
        _claim(module, evaluated_run_ids=("run:001",))
    )

    assert result.claim == "not-evaluated"
    assert result.diagnostic.code == "EVIDENCE_DENOMINATOR_BIAS"


def test_unit_b_does_not_zero_fill_missing_cost_evidence() -> None:
    module = _evidence_module()

    result = module.evaluate_claim(_claim(module, cost=None))

    assert result.claim == "not-evaluated"
    assert result.diagnostic.code == "EVIDENCE_COST_MISSING"


def test_unit_b_reports_missing_prospective_evidence_without_claiming_success() -> None:
    module = _evidence_module()

    result = module.evaluate_claim(_claim(module, prospective_available=False))

    assert result.claim == "not-evaluated"
    assert result.diagnostic.code == "EVIDENCE_PROSPECTIVE_UNAVAILABLE"
