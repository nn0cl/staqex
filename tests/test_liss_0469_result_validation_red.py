"""AT-TDD Phase 1 Red: LISS-0469 result validation/disposition."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _api():
    from compiler.staqex.result_validation import (  # noqa: PLC0415
        ValidationCriteria,
        validate_result,
    )

    return ValidationCriteria, validate_result


def _evidence(**overrides):
    values = {
        "source_fingerprint": "sha256:source",
        "semantic_fingerprint": "sha256:semantic",
        "artifact_fingerprint": "sha256:artifact",
        "raw_result": {"0": 52, "1": 48},
        "baseline": {"0": 50, "1": 50},
        "calibration": {"snapshot": "calibration-not-provided"},
        "noise": {"model": "observed"},
        "provider_anomalies": (),
        "failed_shots": 0,
        "drift_observed": False,
    }
    values.update(overrides)
    return values


def _criteria(**overrides):
    ValidationCriteria, _ = _api()
    values = {
        "version": "validation-v1",
        "metric": "total_variation",
        "maximum_deviation": 0.05,
        "declared_before_run": True,
    }
    values.update(overrides)
    return ValidationCriteria(**values)


def test_valid_result_retains_raw_derived_criteria_and_identity() -> None:
    _, validate = _api()
    result = validate(_evidence(), criteria=_criteria())

    assert result.disposition == "valid-evidence"
    assert result.raw_result == {"0": 52, "1": 48}
    assert result.derived_statistics["metric"] == "total_variation"
    assert result.criteria_version == "validation-v1"
    assert result.source_fingerprint == "sha256:source"
    assert result.artifact_fingerprint == "sha256:artifact"


def test_criteria_must_be_predeclared_and_cannot_be_changed_after_observation() -> None:
    _, validate = _api()
    result = validate(_evidence(), criteria=_criteria(declared_before_run=False))

    assert result.disposition == "inconclusive"
    assert "CRITERIA_NOT_PREDECLARED" in result.diagnostic_codes
    assert result.source_fingerprint == "sha256:source"


def test_drift_failed_shots_or_provider_anomaly_are_explicit_dispositions() -> None:
    _, validate = _api()
    result = validate(
        _evidence(
            drift_observed=True,
            failed_shots=3,
            provider_anomalies=("queue-reported-partial",),
        ),
        criteria=_criteria(),
    )

    assert result.disposition == "inconclusive"
    assert {
        "CALIBRATION_DRIFT",
        "FAILED_SHOTS_PRESENT",
        "PROVIDER_ANOMALY_PRESENT",
    } <= set(result.diagnostic_codes)
    assert result.raw_result == {"0": 52, "1": 48}


def test_large_deviation_is_rejected_without_source_or_identity_rewrite() -> None:
    _, validate = _api()
    result = validate(
        _evidence(raw_result={"0": 95, "1": 5}),
        criteria=_criteria(maximum_deviation=0.05),
    )

    assert result.disposition == "rejected"
    assert "STATISTICAL_DEVIATION_EXCEEDED" in result.diagnostic_codes
    assert result.source_fingerprint == "sha256:source"
    assert result.semantic_fingerprint == "sha256:semantic"
    assert result.artifact_fingerprint == "sha256:artifact"
    assert result.source_rewritten is False


if __name__ == "__main__":
    tests = [
        test_valid_result_retains_raw_derived_criteria_and_identity,
        test_criteria_must_be_predeclared_and_cannot_be_changed_after_observation,
        test_drift_failed_shots_or_provider_anomaly_are_explicit_dispositions,
        test_large_deviation_is_rejected_without_source_or_identity_rewrite,
    ]
    for test in tests:
        test()
    print("OK — LISS-0469 Red contract")
