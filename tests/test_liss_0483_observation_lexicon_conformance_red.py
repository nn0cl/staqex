"""AT-TDD Phase 1 Red: LISS-0483 cross-feature conformance closure."""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source


SPEC = REPO / "docs/specs/staqex-v1-quantum-mental-model-follow-up.md"


def test_conformance_matrix_covers_all_accepted_and_deferred_families() -> None:
    text = SPEC.read_text(encoding="utf-8")

    assert "### 5.6 LISS-0483 cross-feature conformance matrix" in text
    for family in (
        "scientific names",
        "probabilistic composition",
        "coherent composition",
        "controlled operation",
        "migration",
        "observation",
        "terminal boundary",
    ):
        assert family in text
    for field in ("`feature`", "`status`", "`source_id`", "`evidence`", "`diagnostic`"):
        assert field in text


def test_conformance_result_preserves_meaning_and_review_boundary_evidence() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            State view = Inspect(psi)
            Measure view
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    report = compiled.conformance_report
    assert report["feature"] == "observation"
    assert report["status"] == "passed"
    assert report["source_id"]
    assert report["evidence"]["meaning"]
    assert report["evidence"]["review_boundary"]


def test_deferred_conformance_is_inconclusive_or_explicitly_rejected() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Observation<T> report = tomography(plan)
            Measure report
        }
        """
    )

    report = compiled.conformance_report
    assert report["status"] in {"inconclusive", "rejected"}
    assert report["diagnostic"]["code"] == "OBSERVATION_UNSUPPORTED"
    assert report["evidence"]["fabricated_result"] is False
