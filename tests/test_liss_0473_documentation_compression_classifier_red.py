"""AT-TDD Phase 1 Red: LISS-0473 classifier safety contract."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _api():
    from scripts.documentation_compression import (  # noqa: PLC0415
        classify_records,
    )

    return classify_records


def _record(path: str, kind: str = "issue", status: str = "complete", **fields):
    record = {
        "path": path,
        "kind": kind,
        "status": status,
        "referenced_by": [],
        "has_review_evidence": False,
        "indexed": False,
    }
    record.update(fields)
    return record


def test_current_open_work_reference_is_retained_as_evidence() -> None:
    classify = _api()
    result = classify(
        [_record("docs/issues/LISS-0467-run-evidence-reproducibility.md", referenced_by=["open-work-register"])]
    )[0]

    assert result.classification == "retain-evidence"
    assert "open-work-register" in result.reason


def test_completed_current_issue_with_review_packet_is_not_delete_candidate() -> None:
    classify = _api()
    result = classify(
        [_record("docs/issues/LISS-0468-human-authorized-real-qpu-pilot.md", has_review_evidence=True)]
    )[0]

    assert result.classification == "retain-evidence"
    assert result.candidate is False


def test_unresolved_record_is_explicitly_protected() -> None:
    classify = _api()
    result = classify(
        [_record("docs/work-plans/WP-0092-quantum-mental-model-follow-up.md", kind="work-plan", status="open")]
    )[0]

    assert result.classification == "unresolved-review"
    assert result.candidate is False


def test_already_indexed_record_is_not_reclassified_or_deleted() -> None:
    classify = _api()
    result = classify(
        [_record("docs/issues/LISS-0032-typed-second-quantized-operators.md", indexed=True)]
    )[0]

    assert result.classification == "index-pointer"
    assert result.candidate is False
    assert result.reason


def test_only_genuinely_safe_historical_record_is_a_candidate() -> None:
    classify = _api()
    result = classify(
        [_record("docs/issues/LISS-0007-prelude-pi-constant.md", status="complete")]
    )[0]

    assert result.classification == "index-pointer"
    assert result.candidate is True
    assert result.reason


def test_incomplete_status_is_not_treated_as_completed() -> None:
    classify = _api()
    result = classify(
        [_record("docs/issues/LISS-0100-incomplete-record.md", status="incomplete")]
    )[0]

    assert result.classification == "unresolved-review"
    assert result.candidate is False


def test_explicit_negative_completion_status_is_not_a_candidate() -> None:
    classify = _api()
    result = classify(
        [_record("docs/issues/LISS-0101-negative-record.md", status="not complete")]
    )[0]

    assert result.classification == "unresolved-review"
    assert result.candidate is False


def test_filesystem_candidate_scan_uses_conservative_classifier() -> None:
    from scripts.documentation_compression import candidates  # noqa: PLC0415

    candidate_paths = {candidate.path.as_posix() for candidate in candidates()}

    assert "docs/issues/LISS-0468-human-authorized-real-qpu-pilot.md" not in candidate_paths
    assert "docs/issues/LISS-0469-real-qpu-result-validation.md" not in candidate_paths


def test_filesystem_candidate_scan_does_not_treat_current_acceptance_records_as_history() -> None:
    from scripts.documentation_compression import candidates  # noqa: PLC0415

    candidate_paths = {candidate.path.as_posix() for candidate in candidates()}

    assert "docs/issues/LISS-0458-realization-artifact-contract.md" not in candidate_paths
    assert "docs/work-plans/WP-0121-realization-artifact.md" not in candidate_paths


def test_filesystem_candidate_scan_delegates_disposition_to_classifier() -> None:
    import scripts.documentation_compression as compression  # noqa: PLC0415

    calls = []
    original = compression.classify_records

    def observe(records):
        calls.append(records)
        return []

    compression.classify_records = observe
    try:
        compression.candidates()
    finally:
        compression.classify_records = original

    assert calls, "candidates() must delegate disposition to classify_records()"


def test_command_report_preserves_all_dispositions_and_reasons() -> None:
    from scripts.documentation_compression import render_classification_report  # noqa: PLC0415

    report = render_classification_report(
        [
            _record("docs/issues/LISS-0102-canonical.md", status="complete", indexed=True),
            _record(
                "docs/issues/LISS-0103-evidence.md",
                referenced_by=["docs/architecture/open-work-register.md"],
            ),
            _record("docs/issues/LISS-0104-unresolved.md", status="open"),
            _record("docs/issues/LISS-0105-history.md", status="complete"),
        ]
    )

    assert "index-pointer" in report
    assert "retain-evidence" in report
    assert "unresolved-review" in report
    assert "docs/issues/LISS-0105-history.md" in report
    assert "reason=" in report


def test_canonical_record_is_retained_as_canonical() -> None:
    classify = _api()
    result = classify(
        [_record("docs/README.md", status="complete", canonical=True)]
    )[0]

    assert result.classification == "retain-canonical"
    assert result.candidate is False
    assert "canonical" in result.reason.lower()


def test_integrated_scan_preserves_classification_for_safe_candidate() -> None:
    import scripts.documentation_compression as compression  # noqa: PLC0415

    safe_record = _record(
        "docs/issues/LISS-0106-safe-history.md",
        status="complete",
    )
    original = compression._classification_records
    compression._classification_records = lambda texts: [safe_record]
    try:
        candidates = compression.candidates()
    finally:
        compression._classification_records = original

    assert len(candidates) == 1
    assert compression.relative(candidates[0].path) == "docs/issues/LISS-0106-safe-history.md"
    assert candidates[0].classification == "index-pointer"
    assert candidates[0].reason


def test_filesystem_record_builder_includes_canonical_pages() -> None:
    import scripts.documentation_compression as compression  # noqa: PLC0415

    records = compression._classification_records(compression.source_texts())
    canonical_records = {
        str(record["path"]): record
        for record in records
        if record.get("canonical")
    }

    assert "docs/README.md" in canonical_records
    assert "docs/architecture/open-work-register.md" in canonical_records


def test_report_boundary_can_render_all_four_dispositions() -> None:
    from scripts.documentation_compression import render_classification_report  # noqa: PLC0415

    report = render_classification_report(
        [
            _record("docs/README.md", status="complete", canonical=True),
            _record("docs/issues/LISS-0107-evidence.md", referenced_by=["register"]),
            _record("docs/issues/LISS-0108-indexed.md", indexed=True),
            _record("docs/issues/LISS-0109-open.md", status="open"),
        ]
    )

    assert "retain-canonical" in report
    assert "retain-evidence" in report
    assert "index-pointer" in report
    assert "unresolved-review" in report


if __name__ == "__main__":
    tests = [
        test_current_open_work_reference_is_retained_as_evidence,
        test_completed_current_issue_with_review_packet_is_not_delete_candidate,
        test_unresolved_record_is_explicitly_protected,
        test_already_indexed_record_is_not_reclassified_or_deleted,
        test_only_genuinely_safe_historical_record_is_a_candidate,
        test_incomplete_status_is_not_treated_as_completed,
        test_explicit_negative_completion_status_is_not_a_candidate,
        test_filesystem_candidate_scan_uses_conservative_classifier,
        test_filesystem_candidate_scan_does_not_treat_current_acceptance_records_as_history,
        test_filesystem_candidate_scan_delegates_disposition_to_classifier,
        test_command_report_preserves_all_dispositions_and_reasons,
        test_canonical_record_is_retained_as_canonical,
        test_integrated_scan_preserves_classification_for_safe_candidate,
        test_filesystem_record_builder_includes_canonical_pages,
        test_report_boundary_can_render_all_four_dispositions,
    ]
    for test in tests:
        test()
    print("OK — LISS-0473 Red contract")
