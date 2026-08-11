"""Regression guard: LISS-0403 S02 multi-shot benchmark report.

Target: docs/issues/LISS-0403-s02-benchmark-report.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_HOST_DIR = (
    _REPO / "examples" / "showcase" / "S02_drug_discovery" / "host"
)


def _with_host_dir():
    if str(_HOST_DIR) not in sys.path:
        sys.path.insert(0, str(_HOST_DIR))


def test_scoring_discriminates_between_feasible_patterns() -> None:
    """Regression guard for the degenerate-scoring bug caught during
    LISS-0403 design: a symmetric spin-sum formula scored every
    exactly-N-selected pattern identically. Confirms the fixed
    per-candidate scoring actually varies across the feasible set.
    """
    _with_host_dir()
    from classical_baseline import build_predicate_matrices, exact_feasible_patterns
    from scoring import build_candidate_scores, classical_score

    pairwise, diversity = build_predicate_matrices()
    from run_selection import N

    candidate_scores = build_candidate_scores(N)
    feasible = exact_feasible_patterns(pairwise, diversity)
    scores = {classical_score(p, candidate_scores) for p in feasible}
    assert len(scores) > 1, "scoring must discriminate between feasible patterns"


def test_benchmark_report_shape_and_honesty() -> None:
    _with_host_dir()
    from benchmark_report import build_report

    report = build_report(shots=6, base_seed=100)

    assert report.feasibility_verdict == "feasible"
    assert report.terminal_selection is not None
    assert report.baseline_score is not None
    assert report.objective_score is not None
    assert report.reranked_score is not None
    assert report.optimality_claim == "none"

    # Result contract: resource metadata is not fabricated -- every field
    # traces to a value this module actually knows (the .sqx source's own
    # term count, the fixture's own candidate count). LISS-0405: H_obj now
    # evolves psi_sel directly (no separate Suzuki-stepped objective pair).
    assert report.resource_metadata["candidate_count"] == 8
    assert report.resource_metadata["hamiltonian_term_count"] == 44

    qm = report.quality_metrics
    assert qm["shots"] == 6
    # LISS-0406 finding: H_obj's X[i] terms don't commute with `project
    # onto feasible(...)`'s projector (X changes Hamming weight), so a
    # non-vacuum terminal measurement is not automatically feasible --
    # feasibility_rate is verified per shot (scoring.is_feasible), not
    # assumed to be 1.0 "by construction" (that assumption held only for
    # LISS-0402/0403's original disconnected-qubit-pair design).
    assert 0.0 <= qm["feasibility_rate"] <= 1.0
    assert qm["infeasible_shots"] >= 0
    assert qm["reproducibility_verified"] is True
    assert 0.0 <= qm["top_k_overlap"] <= 1.0


def test_benchmark_report_reproducibility_check_detects_real_reruns() -> None:
    _with_host_dir()
    from benchmark_report import check_reproducibility

    assert check_reproducibility(seed=0) is True


def test_feasibility_leak_is_detected_and_excluded_from_scoring() -> None:
    """LISS-0406 finding, regression guard: H_obj's X[i] field terms do
    not commute with `project onto feasible(...)`'s projector, so real
    unitary evolution under it can leak probability outside the feasible
    subspace -- a non-vacuum terminal measurement is not automatically
    feasible. `build_report` must (a) detect this via `scoring.is_feasible`
    rather than assuming every non-vacuum shot is feasible, (b) exclude
    infeasible shots from objective/top-k scoring so they don't corrupt
    the comparison against `baseline_score`/`baseline_top_k` (which are
    themselves computed only over genuinely feasible patterns), and (c)
    warn about it. At the shipped weights (LISS-0406), seeds 0-19 are
    known to include real leakage (confirmed by direct execution)."""
    _with_host_dir()
    from benchmark_report import build_report
    from classical_baseline import (
        DIVERSITY_AT_LEAST,
        EXACTLY_SELECTED,
        build_predicate_matrices,
    )
    from scoring import is_feasible

    report = build_report(shots=20, base_seed=0)
    qm = report.quality_metrics
    assert qm["infeasible_shots"] > 0, (
        "expected the shipped weights/duration to exhibit real feasibility "
        "leakage at seeds 0-19 (confirmed by direct execution during "
        "LISS-0406 design) -- if this no longer reproduces, the leakage "
        "may have been fixed for real (update this test to reflect that) "
        "rather than merely stop showing up by chance"
    )
    assert qm["feasibility_rate"] < 1.0
    assert any("outside the hard-constraint feasible subspace" in w for w in report.warnings)

    pairwise, diversity = build_predicate_matrices()
    assert is_feasible(
        report.terminal_selection,
        pairwise,
        diversity,
        exactly_selected=EXACTLY_SELECTED,
        diversity_at_least=DIVERSITY_AT_LEAST,
    ), "the reported terminal_selection itself must be genuinely feasible"
