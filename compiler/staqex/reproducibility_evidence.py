"""Provider-neutral reproducibility evidence for E01 Unit A."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunManifest:
    manifest_id: str
    source_hash: str
    fixture_hash: str
    input_snapshot_id: str
    model_revision: str
    baseline_revision: str
    seed: int
    numeric_precision: str
    runtime_version: str
    command: str


@dataclass(frozen=True)
class EvidenceRecord:
    manifest: RunManifest
    output_ids: tuple[str, ...]
    numeric_value: float


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str


@dataclass(frozen=True)
class ReplayResult:
    status: str
    diagnostic: Diagnostic | None = None


def _rejected(code: str, message: str) -> ReplayResult:
    return ReplayResult(status="rejected", diagnostic=Diagnostic(code, message))


def _inconclusive(code: str, message: str) -> ReplayResult:
    return ReplayResult(status="inconclusive", diagnostic=Diagnostic(code, message))


def _hashes_match(original: RunManifest, replay: RunManifest) -> bool:
    return (original.source_hash, original.fixture_hash) == (
        replay.source_hash,
        replay.fixture_hash,
    )


def compare_replay(
    original: EvidenceRecord,
    replay: EvidenceRecord,
    *,
    absolute_tolerance: float,
) -> ReplayResult:
    """Compare a replay without silently accepting changed evidence."""

    if not _hashes_match(original.manifest, replay.manifest):
        return _rejected(
            "EVIDENCE_HASH_CHANGED",
            "source or fixture hash changed between runs",
        )
    if original.manifest != replay.manifest:
        return _rejected(
            "EVIDENCE_MANIFEST_MISMATCH",
            "replay manifest identity or inputs differ",
        )
    if original.output_ids != replay.output_ids:
        return _inconclusive(
            "EVIDENCE_OUTPUT_MISMATCH",
            "replay output identity differs",
        )
    if abs(original.numeric_value - replay.numeric_value) > absolute_tolerance:
        return _inconclusive(
            "EVIDENCE_NUMERIC_MISMATCH",
            "numeric value exceeds tolerance",
        )
    return ReplayResult(status="reproduced")
