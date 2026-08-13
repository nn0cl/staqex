"""Regression guard: LISS-0402 S02 end-to-end selection example.

Target: docs/issues/LISS-0402-s02-selection-example.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_SQX = _REPO / "examples" / "showcase" / "S02_drug_discovery" / "main_selection.sqx"
_HOST_DIR = _REPO / "examples" / "showcase" / "S02_drug_discovery" / "host"

from compiler.staqex.pipeline import HARD_CODES, compile_path  # noqa: E402
from compiler.staqex.host import submit_path  # noqa: E402


def test_main_selection_compiles_without_hard_diagnostics() -> None:
    compiled = compile_path(str(_SQX))
    assert compiled.unit is not None
    hard = [d for d in compiled.diagnostics if d.get("code") in HARD_CODES]
    assert not hard, hard


def _predicate_matrices(n: int) -> tuple[list[list[bool]], list[list[float]]]:
    pairwise = [[True] * n for _ in range(n)]
    pairwise[0][1] = pairwise[1][0] = False
    diversity = [[max(0.0, 1.0 - 0.15 * abs(i - j)) for j in range(n)] for i in range(n)]
    return pairwise, diversity


def _run_seed(seed: int, pairwise, diversity, activity_w, selectivity_w):
    return submit_path(
        str(_SQX),
        settings={
            "seed": seed,
            "inputs": {
                "pairwise_compatible": pairwise,
                "diversity": diversity,
                "activity_weights": activity_w,
                "selectivity_weights": selectivity_w,
            },
        },
    ).result()


def test_main_selection_runs_and_some_seeds_respect_feasibility() -> None:
    """LISS-0406 finding: H_obj's X[i] field terms don't commute with
    `project onto feasible(...)`'s projector (X changes a candidate's
    selected bit, so it changes Hamming weight), so real unitary
    evolution under H_obj can leak probability outside the projected
    feasible subspace -- a non-Vacuum terminal measurement is not
    unconditionally feasible (superseding this test's original LISS-0402
    assumption, which held only for the pre-LISS-0405 disconnected
    objective-qubit-pair design). This test verifies the program still
    runs and produces well-formed selections across several seeds, and
    that at least one of them is genuinely feasible -- not that every
    one is."""
    sys.path.insert(0, str(_HOST_DIR))
    try:
        from run_selection import build_objective_weight_arrays
    finally:
        sys.path.remove(str(_HOST_DIR))
    pairwise, diversity = _predicate_matrices(8)
    activity_w, selectivity_w = build_objective_weight_arrays()

    any_feasible = False
    for seed in range(5):
        result = _run_seed(seed, pairwise, diversity, activity_w, selectivity_w)
        assert result.status == "succeeded", result.diagnostics
        assert result.measurements
        envelope = result.measurements[0]
        assert envelope.vacuum is False
        pattern = envelope.value
        assert len(pattern) == 8
        assert all(bit in (0, 1) for bit in pattern)
        selected = [i for i, bit in enumerate(pattern) if bit]
        if sum(pattern) != 3:
            continue
        if any(
            not pairwise[i][j] for i in selected for j in selected if i < j
        ):
            continue
        if len(selected) >= 2:
            import itertools

            min_div = min(
                diversity[i][j] for i, j in itertools.combinations(selected, 2)
            )
            if min_div < 0.3:
                continue
        any_feasible = True
    assert any_feasible, "expected at least one feasible outcome across 5 seeds"


def test_classical_baseline_agrees_on_feasible_set() -> None:
    sys.path.insert(0, str(_HOST_DIR))
    try:
        from classical_baseline import EXACTLY_SELECTED, exact_feasible_patterns
        from run_selection import build_predicate_matrices

        pairwise, diversity = build_predicate_matrices()
        feasible = exact_feasible_patterns(pairwise, diversity)
        assert feasible, "baseline must find at least one feasible pattern"
        assert all(sum(p) == EXACTLY_SELECTED for p in feasible)
    finally:
        sys.path.remove(str(_HOST_DIR))
