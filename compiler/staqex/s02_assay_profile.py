"""Bounded S02 biochemical IC50 assay-profile curation contract.

This module is deliberately host-side.  It validates a frozen input snapshot,
creates a new curated revision, and quarantines records whose scientific
identity or meaning cannot be preserved.  It does not download data, perform
chemistry normalization, fit a model, or submit to a quantum provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


_RELATIONS = {"=", "<", ">"}
_PROFILE_ENDPOINT = "IC50"
_PROFILE_UNIT = "nM"
_PROFILE_FAMILY = "biochemical-inhibition"


@dataclass(frozen=True)
class AssayDiagnostic:
    """A stable, machine-readable reason for rejecting a snapshot."""

    code: str
    message: str


def _immutable_record(record: Mapping[str, Any]) -> Mapping[str, Any]:
    return MappingProxyType(dict(record))


@dataclass(frozen=True)
class FrozenAssaySnapshot:
    """Raw source records and provenance, retained without mutation."""

    metadata: Mapping[str, Any]
    records: tuple[Mapping[str, Any], ...]
    revision: int = 1

def __post_init__(self) -> None:
        if isinstance(self.revision, bool) or self.revision < 1:
            raise ValueError("snapshot revision must be positive")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        object.__setattr__(
            self,
            "records",
            tuple(_immutable_record(record) for record in self.records),
        )


@dataclass(frozen=True)
class AssayCurationResult:
    """A curated revision or an explicit quarantine result."""

    status: str
    revision: int
    records: tuple[Mapping[str, Any], ...]
    raw_snapshot_id: str
    diagnostic: AssayDiagnostic | None = None


def _quarantine(
    snapshot: FrozenAssaySnapshot,
    code: str,
    message: str,
) -> AssayCurationResult:
    return AssayCurationResult(
        status="quarantine",
        revision=snapshot.revision + 1,
        records=snapshot.records,
        raw_snapshot_id=str(snapshot.metadata.get("source_id", "")),
        diagnostic=AssayDiagnostic(code=code, message=message),
    )


def _provenance_is_verified(metadata: Mapping[str, Any]) -> bool:
    checksum = metadata.get("checksum")
    license_status = metadata.get("license_status")
    return bool(checksum) and license_status in {"verified", "verified-for-test"}


def _identity_collision(
    records: tuple[Mapping[str, Any], ...],
) -> bool:
    identities: dict[str, set[tuple[Any, ...]]] = {}
    for record in records:
        activity_id = record.get("activity_id")
        identity = (
            record.get("compound_id"),
            record.get("target_id"),
            record.get("assay_id"),
        )
        identities.setdefault(str(activity_id), set()).add(identity)
    return any(len(values) > 1 for values in identities.values())


def _replicate_collision(
    records: tuple[Mapping[str, Any], ...],
) -> bool:
    identities: dict[str, set[tuple[Any, ...]]] = {}
    for record in records:
        replicate_id = record.get("replicate_id")
        identity = (record.get("compound_id"), record.get("activity_id"))
        identities.setdefault(str(replicate_id), set()).add(identity)
    return any(len(values) > 1 for values in identities.values())


def _record_diagnostic(
    record: Mapping[str, Any],
    *,
    target_id: str,
) -> AssayDiagnostic | None:
    """Return the first record-level contract violation, if any."""

    checks = (
        (
            record.get("endpoint") != _PROFILE_ENDPOINT,
            "ASSAY_ENDPOINT_MISMATCH",
            "record endpoint is outside the approved IC50 profile",
        ),
        (
            record.get("unit") != _PROFILE_UNIT,
            "ASSAY_UNIT_MISMATCH",
            "record unit is not nM",
        ),
        (
            record.get("relation") not in _RELATIONS,
            "ASSAY_RELATION_LOSS",
            "record relation must preserve =, <, or >",
        ),
        (
            record.get("target_id") != target_id,
            "ASSAY_ENDPOINT_MISMATCH",
            "record target is outside the selected profile",
        ),
    )
    for failed, code, message in checks:
        if failed:
            return AssayDiagnostic(code=code, message=message)
    return None


def curate_snapshot(
    snapshot: FrozenAssaySnapshot,
    *,
    target_id: str,
    assay_family: str,
    endpoint: str,
) -> AssayCurationResult:
    """Validate one bounded IC50 profile and create its next revision."""

    if not _provenance_is_verified(snapshot.metadata):
        return _quarantine(
            snapshot,
            "ASSAY_SOURCE_LICENSE_MISSING",
            "snapshot requires a checksum and verified license status",
        )

    if assay_family != _PROFILE_FAMILY or endpoint != _PROFILE_ENDPOINT:
        return _quarantine(
            snapshot,
            "ASSAY_ENDPOINT_MISMATCH",
            "snapshot does not match the approved biochemical IC50 profile",
        )

    for record in snapshot.records:
        diagnostic = _record_diagnostic(record, target_id=target_id)
        if diagnostic is not None:
            return _quarantine(
                snapshot,
                diagnostic.code,
                diagnostic.message,
            )

    if _identity_collision(snapshot.records):
        return _quarantine(
            snapshot,
            "ASSAY_IDENTITY_COLLISION",
            "one activity ID refers to multiple compound/target/assay identities",
        )

    if _replicate_collision(snapshot.records):
        return _quarantine(
            snapshot,
            "ASSAY_REPLICATE_MISMATCH",
            "one replicate ID refers to multiple activity identities",
        )

    return AssayCurationResult(
        status="accepted",
        revision=snapshot.revision + 1,
        records=snapshot.records,
        raw_snapshot_id=str(snapshot.metadata["source_id"]),
    )
