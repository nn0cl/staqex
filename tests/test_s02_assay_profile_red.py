"""Phase 1 Red tests for WP-0134 / LISS-0517 D01.

The assay-profile module is intentionally absent until Phase 2.  Fixtures are
small, deterministic contract examples and are not real scientific results.
"""

from __future__ import annotations

import importlib

import pytest


SNAPSHOT = {
    "source_id": "fixture:assay-source-01",
    "checksum": "sha256:fixture-assay-01",
    "license_status": "verified-for-test",
    "acquired_at": "2026-09-08T00:00:00Z",
    "profile_version": "assay-ic50-v1",
}


def _assay_module():
    try:
        return importlib.import_module("compiler.staqex.s02_assay_profile")
    except ModuleNotFoundError as error:
        pytest.fail(
            "LISS-0517 requires compiler.staqex.s02_assay_profile: "
            "D01 assay profile is not implemented yet"
        )
        raise AssertionError from error


def _record(**overrides):
    record = {
        "compound_id": "compound:001",
        "target_id": "target:001",
        "assay_id": "assay:001",
        "activity_id": "activity:001",
        "endpoint": "IC50",
        "relation": "=",
        "value": 12.5,
        "unit": "nM",
        "replicate_id": "replicate:001",
        "source_id": SNAPSHOT["source_id"],
    }
    record.update(overrides)
    return record


def test_d01_accepts_one_measured_ic50_activity_without_editing_raw_snapshot() -> None:
    module = _assay_module()
    raw = module.FrozenAssaySnapshot(
        metadata=SNAPSHOT,
        records=(_record(),),
    )

    curated = module.curate_snapshot(raw, target_id="target:001", assay_family="biochemical-inhibition", endpoint="IC50")

    assert curated.revision > raw.revision
    assert curated.records[0].activity_id == "activity:001"
    assert curated.records[0].relation == "="
    assert raw.records[0].value == 12.5


def test_d01_preserves_censored_relation_instead_of_turning_it_into_equality() -> None:
    module = _assay_module()
    raw = module.FrozenAssaySnapshot(
        metadata=SNAPSHOT,
        records=(_record(relation="<", value=0.1, activity_id="activity:below"),),
    )

    curated = module.curate_snapshot(raw, target_id="target:001", assay_family="biochemical-inhibition", endpoint="IC50")

    assert curated.records[0].relation == "<"
    assert curated.records[0].value == 0.1


@pytest.mark.parametrize(
    "records, expected_code",
    [
        ((_record(endpoint="Ki"),), "ASSAY_ENDPOINT_MISMATCH"),
        ((_record(unit="uM"),), "ASSAY_UNIT_MISMATCH"),
        ((_record(), _record(compound_id="compound:002", activity_id="activity:002")), "ASSAY_REPLICATE_MISMATCH"),
    ],
)
def test_d01_quarantines_incompatible_endpoint_unit_and_replicate_identity(
    records: tuple[dict[str, object], ...], expected_code: str
) -> None:
    module = _assay_module()
    raw = module.FrozenAssaySnapshot(metadata=SNAPSHOT, records=records)

    result = module.curate_snapshot(
        raw,
        target_id="target:001",
        assay_family="biochemical-inhibition",
        endpoint="IC50",
    )

    assert result.status == "quarantine"
    assert result.diagnostic.code == expected_code
    assert result.raw_snapshot_id == SNAPSHOT["source_id"]


def test_d01_quarantines_an_identity_collision_without_merging_compounds() -> None:
    module = _assay_module()
    raw = module.FrozenAssaySnapshot(
        metadata=SNAPSHOT,
        records=(
            _record(activity_id="activity:001", compound_id="compound:001"),
            _record(activity_id="activity:001", compound_id="compound:002", assay_id="assay:002"),
        ),
    )

    result = module.curate_snapshot(
        raw,
        target_id="target:001",
        assay_family="biochemical-inhibition",
        endpoint="IC50",
    )

    assert result.status == "quarantine"
    assert result.diagnostic.code == "ASSAY_IDENTITY_COLLISION"
    assert {record.compound_id for record in result.records} == {"compound:001", "compound:002"}


def test_d01_quarantines_a_snapshot_without_verified_license_or_checksum() -> None:
    module = _assay_module()
    metadata = {**SNAPSHOT, "checksum": None, "license_status": "unknown"}
    raw = module.FrozenAssaySnapshot(metadata=metadata, records=(_record(),))

    result = module.curate_snapshot(
        raw,
        target_id="target:001",
        assay_family="biochemical-inhibition",
        endpoint="IC50",
    )

    assert result.status == "quarantine"
    assert result.diagnostic.code == "ASSAY_SOURCE_LICENSE_MISSING"
