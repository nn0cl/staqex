"""Leakage-safe split and provenance boundary for the S02 model workflow.

The module records the scientific data boundary around a model.  It is not a
model implementation: fitting and prediction values remain supplied by a
future provider-neutral ModelPort.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from types import MappingProxyType
from typing import Any, Mapping


_PARTITIONS = ("train", "validation", "holdout")
_MODEL_REVISION = "model:unimplemented-v1"


@dataclass(frozen=True)
class LeakageDiagnostic:
    code: str
    message: str


@dataclass(frozen=True)
class SplitProfile:
    profile_id: str
    availability_cutoff: str
    train_record_ids: tuple[str, ...]
    validation_record_ids: tuple[str, ...]
    holdout_record_ids: tuple[str, ...]

    def partition_ids(self) -> Mapping[str, tuple[str, ...]]:
        return MappingProxyType(
            {
                "train": self.train_record_ids,
                "validation": self.validation_record_ids,
                "holdout": self.holdout_record_ids,
            }
        )


@dataclass(frozen=True)
class SplitResult:
    status: str
    split_profile_id: str
    availability_cutoff: str
    partitions: Mapping[str, tuple[str, ...]]
    records: tuple[Mapping[str, Any], ...]
    diagnostic: LeakageDiagnostic | None = None


@dataclass(frozen=True)
class FitRecord:
    id: str
    model_revision: str
    split_profile_id: str
    train_record_ids: tuple[str, ...]
    transform_fit_record_ids: tuple[str, ...]
    feature_selection_record_ids: tuple[str, ...]
    holdout_label_ids: tuple[str, ...]
    availability_cutoff: str


@dataclass(frozen=True)
class FitResult:
    status: str
    fit_record: FitRecord
    diagnostic: LeakageDiagnostic | None = None


@dataclass(frozen=True)
class Prediction:
    candidate_id: str
    value: float
    uncertainty: float | None
    applicability: str
    fit_record_id: str


def _quarantine(
    profile_id: str,
    code: str,
    message: str,
) -> SplitResult:
    return SplitResult(
        status="quarantine",
        split_profile_id=profile_id,
        availability_cutoff="",
        partitions=MappingProxyType({partition: () for partition in _PARTITIONS}),
        records=(),
        diagnostic=LeakageDiagnostic(code=code, message=message),
    )


def _timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("available_at must be an ISO-8601 timestamp")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _assigned_groups(
    records: Mapping[str, Mapping[str, Any]],
    partitions: Mapping[str, tuple[str, ...]],
) -> bool:
    groups: dict[str, str] = {}
    for partition, record_ids in partitions.items():
        for record_id in record_ids:
            record = records[record_id]
            for field in ("compound_id", "replicate_group_id"):
                group_id = record.get(field)
                prior = groups.get(f"{field}:{group_id}")
                if prior is not None and prior != partition:
                    return True
                groups[f"{field}:{group_id}"] = partition
    return False


def build_split(
    records: tuple[Mapping[str, Any], ...],
    profile: SplitProfile,
) -> SplitResult:
    """Validate a predeclared group split without reshuffling records."""

    by_id: dict[str, Mapping[str, Any]] = {}
    for record in records:
        record_id = record.get("record_id")
        if not isinstance(record_id, str) or record_id in by_id:
            return _quarantine(
                profile.profile_id,
                "MODEL_FIT_HISTORY_INCOMPLETE",
                "split records require unique record IDs",
            )
        by_id[record_id] = MappingProxyType(dict(record))

    partitions: dict[str, tuple[str, ...]] = {}
    seen_partition: dict[str, str] = {}
    try:
        cutoff = _timestamp(profile.availability_cutoff)
    except ValueError:
        return _quarantine(
            profile.profile_id,
            "MODEL_CUTOFF_LEAKAGE",
            "availability cutoff must be an ISO-8601 timestamp",
        )

    for partition, profile_ids in profile.partition_ids().items():
        present_ids = tuple(record_id for record_id in profile_ids if record_id in by_id)
        partitions[partition] = present_ids
        for record_id in present_ids:
            prior_partition = seen_partition.get(record_id)
            if prior_partition is not None and prior_partition != partition:
                return _quarantine(
                    profile.profile_id,
                    "MODEL_SPLIT_GROUP_OVERLAP",
                    "one record ID is assigned to multiple partitions",
                )
            seen_partition[record_id] = partition
            try:
                if _timestamp(by_id[record_id].get("available_at")) > cutoff:
                    return _quarantine(
                        profile.profile_id,
                        "MODEL_CUTOFF_LEAKAGE",
                        "a partition record is unavailable at the fixed cutoff",
                    )
            except ValueError:
                return _quarantine(
                    profile.profile_id,
                    "MODEL_CUTOFF_LEAKAGE",
                    "partition record has an invalid availability timestamp",
                )

    if _assigned_groups(by_id, partitions):
        return _quarantine(
            profile.profile_id,
            "MODEL_SPLIT_GROUP_OVERLAP",
            "compound or replicate group crosses split partitions",
        )

    selected = tuple(by_id[record_id] for record_id in seen_partition)
    return SplitResult(
        status="accepted",
        split_profile_id=profile.profile_id,
        availability_cutoff=profile.availability_cutoff,
        partitions=MappingProxyType(partitions),
        records=selected,
    )


def fit_model(
    split: SplitResult,
    *,
    feature_fit_record_ids: tuple[str, ...],
) -> FitResult:
    """Create fit provenance while preventing non-train feature fitting."""

    train_ids = split.partitions.get("train", ())
    if split.status != "accepted":
        diagnostic = split.diagnostic or LeakageDiagnostic(
            "MODEL_FIT_HISTORY_INCOMPLETE", "cannot fit a quarantined split"
        )
        return _quarantined_fit(split, diagnostic)

    if any(record_id not in train_ids for record_id in feature_fit_record_ids):
        diagnostic = LeakageDiagnostic(
            "MODEL_FEATURE_FIT_LEAKAGE",
            "feature fitting may use train records only",
        )
        return _quarantined_fit(split, diagnostic)

    return FitResult(status="accepted", fit_record=_fit_record(split, train_ids))


def _fit_record(
    split: SplitResult,
    train_record_ids: tuple[str, ...],
) -> FitRecord:
    return FitRecord(
        id=f"fit:{split.split_profile_id}:v1",
        model_revision=_MODEL_REVISION,
        split_profile_id=split.split_profile_id,
        train_record_ids=train_record_ids,
        transform_fit_record_ids=train_record_ids,
        feature_selection_record_ids=(),
        holdout_label_ids=(),
        availability_cutoff=split.availability_cutoff,
    )


def _empty_fit(split: SplitResult) -> FitRecord:
    return FitRecord(
        id=f"fit:{split.split_profile_id}:quarantine",
        model_revision=_MODEL_REVISION,
        split_profile_id=split.split_profile_id,
        train_record_ids=(),
        transform_fit_record_ids=(),
        feature_selection_record_ids=(),
        holdout_label_ids=(),
        availability_cutoff="",
    )


def _quarantined_fit(
    split: SplitResult,
    diagnostic: LeakageDiagnostic,
) -> FitResult:
    return FitResult(
        status="quarantine",
        fit_record=_empty_fit(split),
        diagnostic=diagnostic,
    )


def predict(
    fit: FitResult,
    *,
    candidate_id: str,
    value: float,
    uncertainty: float | None,
    applicability: str,
) -> Prediction:
    """Attach prediction evidence to a fit revision without reclassifying it."""

    if fit.status != "accepted":
        raise ValueError("cannot predict from a quarantined fit")
    return Prediction(
        candidate_id=candidate_id,
        value=value,
        uncertainty=uncertainty,
        applicability=applicability,
        fit_record_id=fit.fit_record.id,
    )
