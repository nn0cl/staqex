"""AT-TDD Phase 1 Red: LISS-0474 classifier maintenance contract."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def test_legacy_historical_candidate_path_is_removed() -> None:
    source = (REPO / "scripts/documentation_compression.py").read_text(encoding="utf-8")

    assert "def historical_candidate" not in source


def test_review_evidence_detection_accepts_repository_relative_review_path() -> None:
    from scripts.documentation_compression import _record_has_review_evidence  # noqa: PLC0415

    record = Path("docs/issues/LISS-0474-documentation-compression-maintenance.md")
    review = Path("docs/collaboration/reviews/liss-0474-review.md")
    texts = {
        record: "# LISS-0474\n",
        review: "Review evidence for LISS-0474\n",
    }

    assert _record_has_review_evidence(record, texts) is True


def test_candidates_still_use_the_conservative_classifier() -> None:
    import scripts.documentation_compression as compression  # noqa: PLC0415

    source = (REPO / "scripts/documentation_compression.py").read_text(encoding="utf-8")

    assert "classify_records(records)" in source
    assert compression.candidates() == []


if __name__ == "__main__":
    for test in (
        test_legacy_historical_candidate_path_is_removed,
        test_review_evidence_detection_accepts_repository_relative_review_path,
        test_candidates_still_use_the_conservative_classifier,
    ):
        test()
    print("OK — LISS-0474 Red contract")
