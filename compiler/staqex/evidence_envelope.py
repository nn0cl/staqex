"""Local/fake run evidence envelope with explicit reproducibility status."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class EvidenceRequirements:
    version: str


@dataclass(frozen=True)
class EvidenceEnvelope:
    status: str
    version: str
    source_fingerprint: str | None
    semantic_fingerprint: str | None
    artifact_fingerprint: str | None
    target_profile: str | None
    provider_id: str | None
    device_id: str | None
    job_id: str | None
    compiler_version: str | None
    sdk_version: str | None
    shots: int | None
    seed: int | None
    calibration: object
    noise: object
    started_at: str | None
    completed_at: str | None
    cost: object
    capability_profile: str | None
    baseline: Mapping[str, Any]
    tolerance: Mapping[str, Any]
    drift_policy: str | None
    evidence_kind: str | None
    physical_execution_claimed: bool
    fidelity_claim: str
    diagnostic_codes: tuple[str, ...]


def _missing_identity(fields: Mapping[str, Any]) -> list[str]:
    missing: list[str] = []
    if not fields.get("artifact_fingerprint"):
        missing.append("ARTIFACT_FINGERPRINT_MISSING")
    if not fields.get("job_id"):
        missing.append("JOB_ID_MISSING")
    return missing


def _envelope_status(diagnostics: list[str]) -> str:
    if "DRIFT_UNEXPLAINED" in diagnostics:
        return "inconclusive"
    return "incomplete" if diagnostics else "complete"


def _fidelity_claim() -> str:
    return "not-established"


def build_evidence_envelope(
    fields: Mapping[str, Any],
    *,
    requirements: EvidenceRequirements,
) -> EvidenceEnvelope:
    """Build an envelope from local/fake evidence without inventing facts."""
    diagnostics = _missing_identity(fields)
    if fields.get("drift_observed") and not fields.get("calibration"):
        diagnostics.append("DRIFT_UNEXPLAINED")
    status = _envelope_status(diagnostics)
    evidence_kind = fields.get("evidence_kind")
    fidelity_claim = _fidelity_claim()
    return EvidenceEnvelope(
        status=status,
        version=requirements.version,
        source_fingerprint=fields.get("source_fingerprint"),
        semantic_fingerprint=fields.get("semantic_fingerprint"),
        artifact_fingerprint=fields.get("artifact_fingerprint"),
        target_profile=fields.get("target_profile"),
        provider_id=fields.get("provider_id"),
        device_id=fields.get("device_id"),
        job_id=fields.get("job_id"),
        compiler_version=fields.get("compiler_version"),
        sdk_version=fields.get("sdk_version"),
        shots=fields.get("shots"),
        seed=fields.get("seed"),
        calibration=fields.get("calibration"),
        noise=fields.get("noise"),
        started_at=fields.get("started_at"),
        completed_at=fields.get("completed_at"),
        cost=fields.get("cost"),
        capability_profile=fields.get("capability_profile"),
        baseline=dict(fields.get("baseline", {})),
        tolerance=dict(fields.get("tolerance", {})),
        drift_policy=fields.get("drift_policy"),
        evidence_kind=evidence_kind,
        physical_execution_claimed=bool(fields.get("physical_execution_claimed", False)),
        fidelity_claim=fidelity_claim,
        diagnostic_codes=tuple(diagnostics),
    )


__all__ = ["EvidenceEnvelope", "EvidenceRequirements", "build_evidence_envelope"]
