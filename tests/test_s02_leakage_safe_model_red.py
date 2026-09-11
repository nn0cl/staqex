"""Phase 1 Red tests for WP-0135 / LISS-0518 D02."""

from __future__ import annotations

import importlib

import pytest


CUTOFF = "2025-01-01T00:00:00Z"


def _model_module():
    try:
        return importlib.import_module("compiler.staqex.s02_leakage_safe_model")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0518 D02 implementation is not present yet")
        raise AssertionError from error


def _record(record_id: str, **overrides: object) -> dict[str, object]:
    record = {
        "record_id": record_id,
        "compound_id": "compound:001",
        "replicate_group_id": "replicate-group:001",
        "activity_id": f"activity:{record_id}",
        "available_at": "2024-06-01T00:00:00Z",
        "round_id": "round:001",
        "label": 12.5,
    }
    record.update(overrides)
    return record


def _profile(module):
    return module.SplitProfile(
        profile_id="split:s02-v1",
        availability_cutoff=CUTOFF,
        train_record_ids=("record:train",),
        validation_record_ids=("record:validation",),
        holdout_record_ids=("record:holdout",),
    )


def test_d02_builds_fixed_group_split_without_cross_partition_records() -> None:
    module = _model_module()
    records = (
        _record("record:train", compound_id="compound:001", replicate_group_id="group:001"),
        _record("record:validation", compound_id="compound:002", replicate_group_id="group:002"),
        _record("record:holdout", compound_id="compound:003", replicate_group_id="group:003"),
    )

    result = module.build_split(records, _profile(module))

    assert result.status == "accepted"
    assert result.partitions["train"] == ("record:train",)
    assert result.partitions["validation"] == ("record:validation",)
    assert result.partitions["holdout"] == ("record:holdout",)
    assert result.split_profile_id == "split:s02-v1"


@pytest.mark.parametrize(
    "records, expected_code",
    [
        (
            (
                _record("record:train", compound_id="compound:001", replicate_group_id="group:001"),
                _record("record:validation", compound_id="compound:001", replicate_group_id="group:001"),
                _record("record:holdout", compound_id="compound:003", replicate_group_id="group:003"),
            ),
            "MODEL_SPLIT_GROUP_OVERLAP",
        ),
        (
            (
                _record("record:train"),
                _record("record:validation", compound_id="compound:002", replicate_group_id="group:002", available_at="2025-01-02T00:00:00Z", round_id="round:002"),
                _record("record:holdout", compound_id="compound:003", replicate_group_id="group:003"),
            ),
            "MODEL_CUTOFF_LEAKAGE",
        ),
    ],
)
def test_d02_quarantines_group_overlap_and_cutoff_leakage(
    records: tuple[dict[str, object], ...], expected_code: str
) -> None:
    module = _model_module()
    result = module.build_split(records, _profile(module))

    assert result.status == "quarantine"
    assert result.diagnostic.code == expected_code


def test_d02_fit_history_excludes_holdout_labels_and_records_fit_inputs() -> None:
    module = _model_module()
    records = (
        _record("record:train"),
        _record("record:validation", compound_id="compound:002", replicate_group_id="group:002"),
        _record("record:holdout", compound_id="compound:003", replicate_group_id="group:003"),
    )
    split = module.build_split(records, _profile(module))
    fit = module.fit_model(split, feature_fit_record_ids=("record:train",))

    assert fit.fit_record.train_record_ids == ("record:train",)
    assert fit.fit_record.transform_fit_record_ids == ("record:train",)
    assert fit.fit_record.feature_selection_record_ids == ()
    assert fit.fit_record.holdout_label_ids == ()


def test_d02_rejects_feature_fit_history_that_contains_holdout_records() -> None:
    module = _model_module()
    records = (
        _record("record:train"),
        _record("record:validation", compound_id="compound:002", replicate_group_id="group:002"),
        _record("record:holdout", compound_id="compound:003", replicate_group_id="group:003"),
    )
    split = module.build_split(records, _profile(module))
    result = module.fit_model(split, feature_fit_record_ids=("record:train", "record:holdout"))

    assert result.status == "quarantine"
    assert result.diagnostic.code == "MODEL_FEATURE_FIT_LEAKAGE"


def test_d02_prediction_keeps_uncertainty_applicability_and_fit_provenance() -> None:
    module = _model_module()
    split = module.build_split((_record("record:train"),), _profile(module))
    fit = module.fit_model(split, feature_fit_record_ids=("record:train",))
    prediction = module.predict(
        fit,
        candidate_id="compound:candidate",
        value=10.0,
        uncertainty=1.5,
        applicability="in-domain",
    )

    assert prediction.fit_record_id == fit.fit_record.id
    assert prediction.value == 10.0
    assert prediction.uncertainty == 1.5
    assert prediction.applicability == "in-domain"
