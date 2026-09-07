"""Shared classical scoring for S02 selection patterns (LISS-0403).

Used by both the exact classical baseline and the benchmark report so
the two always score patterns identically -- a real, reusable comparison
basis, not two independently-drifting implementations of "the same"
formula.

Per-candidate synthetic scores (not a symmetric spin-sum formula): an
earlier version of this module scored `sum(spins)*W_a +
sum_pairs(spins_i*spins_j)*W_d`, which is a well-known combinatorial
identity (`sum_pairs(s_i s_j) = ((sum s)^2 - n) / 2` for `s_i = +/-1`) --
once `exactly_selected` fixes `sum(spins)`, that formula is *constant*
across every feasible pattern. Confirmed by direct computation: every
3-of-8 pattern scored exactly the same. Replaced with per-candidate
`activity`/`selectivity` values so different patterns actually score
differently -- a real bug caught before it silently made every quality
metric in the benchmark report meaningless.
"""

from __future__ import annotations

import itertools

ACTIVITY_WEIGHT = 0.45
SELECTIVITY_WEIGHT = 0.30


def build_candidate_scores(n: int) -> list[tuple[float, float]]:
    """Toy synthetic per-candidate (activity, selectivity) scores in
    [0, 1] -- a deterministic proxy, not real chemistry, matching the
    spec's own "synthetic fixture for the first implementation" fixture
    rule. Candidate identity never crosses into the Kernel (spec
    boundary contract); this stays entirely Host-side.
    """
    return [
        (0.30 + 0.08 * (i % 5), 0.20 + 0.07 * ((i * 3) % 5)) for i in range(n)
    ]


def classical_score(
    pattern: tuple[int, ...], candidate_scores: list[tuple[float, float]]
) -> float:
    """Weighted sum of the selected candidates' own activity/selectivity
    scores -- discriminates between different feasible patterns, unlike
    a symmetric spin-sum formula (see module docstring)."""
    selected = [i for i, bit in enumerate(pattern) if bit]
    activity = sum(candidate_scores[i][0] for i in selected) * ACTIVITY_WEIGHT
    selectivity = sum(candidate_scores[i][1] for i in selected) * SELECTIVITY_WEIGHT
    return activity + selectivity


def is_feasible(
    pattern: tuple[int, ...],
    pairwise: list[list[bool]],
    diversity: list[list[float]],
    *,
    exactly_selected: int,
    diversity_at_least: float,
) -> bool:
    if sum(pattern) != exactly_selected:
        return False
    selected = [i for i, bit in enumerate(pattern) if bit]
    for i, j in itertools.combinations(selected, 2):
        if not pairwise[i][j]:
            return False
    pairs = list(itertools.combinations(selected, 2))
    if pairs and min(diversity[i][j] for i, j in pairs) < diversity_at_least:
        return False
    return True


__all__ = [
    "ACTIVITY_WEIGHT",
    "SELECTIVITY_WEIGHT",
    "build_candidate_scores",
    "classical_score",
    "is_feasible",
]
