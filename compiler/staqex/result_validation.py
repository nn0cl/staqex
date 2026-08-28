"""Offline validation and disposition of provider-neutral result evidence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class ValidationCriteria:
    version: str
    metric: str
    maximum_deviation: float
    declared_before_run: bool


@dataclass(frozen=True)
class ValidationResult:
    disposition: str
    raw_result: Mapping[str, Any]
    derived_statistics: Mapping[str, Any]
    criteria_version: str
    source_fingerprint: str | None
    semantic_fingerprint: str | None
    artifact_fingerprint: str | None
    diagnostic_codes: tuple[str, ...]
    source_rewritten: bool = False


def _total_variation(raw: Mapping[str, Any], baseline: Mapping[str, Any]) -> float:
    keys = set(raw) | set(baseline)
    return 0.5 * sum(abs(float(raw.get(key, 0)) - float(baseline.get(key, 0))) for key in keys) / 100


def _diagnostics(
    evidence: Mapping[str, Any], criteria: ValidationCriteria
) -> list[str]:
    diagnostics: list[str] = []
    if not criteria.declared_before_run:
        diagnostics.append("CRITERIA_NOT_PREDECLARED")
    if evidence.get("drift_observed"):
        diagnostics.append("CALIBRATION_DRIFT")
    if evidence.get("failed_shots", 0):
        diagnostics.append("FAILED_SHOTS_PRESENT")
    if evidence.get("provider_anomalies"):
        diagnostics.append("PROVIDER_ANOMALY_PRESENT")
    return diagnostics


def _disposition(diagnostics: list[str]) -> str:
    if "CRITERIA_NOT_PREDECLARED" in diagnostics:
        return "inconclusive"
    if any(
        code in diagnostics
        for code in ("CALIBRATION_DRIFT", "FAILED_SHOTS_PRESENT", "PROVIDER_ANOMALY_PRESENT")
    ):
        return "inconclusive"
    if "STATISTICAL_DEVIATION_EXCEEDED" in diagnostics:
        return "rejected"
    return "valid-evidence"


def _derived_statistics(
    raw: Mapping[str, Any], baseline: Mapping[str, Any], criteria: ValidationCriteria
) -> dict[str, Any]:
    return {
        "metric": criteria.metric,
        "deviation": _total_variation(raw, baseline),
        "baseline": baseline,
        "sample_count": sum(int(value) for value in raw.values()) if raw else 0,
    }


def validate_result(
    evidence: Mapping[str, Any], *, criteria: ValidationCriteria
) -> ValidationResult:
    raw = dict(evidence.get("raw_result", {}))
    baseline = dict(evidence.get("baseline", {}))
    deviation = _total_variation(raw, baseline)
    diagnostics = _diagnostics(evidence, criteria)
    if deviation > criteria.maximum_deviation:
        diagnostics.append("STATISTICAL_DEVIATION_EXCEEDED")
    disposition = _disposition(diagnostics)
    derived = _derived_statistics(raw, baseline, criteria)
    return ValidationResult(
        disposition=disposition,
        raw_result=raw,
        derived_statistics=derived,
        criteria_version=criteria.version,
        source_fingerprint=evidence.get("source_fingerprint"),
        semantic_fingerprint=evidence.get("semantic_fingerprint"),
        artifact_fingerprint=evidence.get("artifact_fingerprint"),
        diagnostic_codes=tuple(dict.fromkeys(diagnostics)),
    )


__all__ = ["ValidationCriteria", "ValidationResult", "validate_result"]
