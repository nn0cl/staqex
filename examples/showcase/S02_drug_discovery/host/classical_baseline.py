#!/usr/bin/env python3
"""Classical baseline for main_selection.sqx (LISS-0402/0403, design doc §7
"Baseline discipline"): brute-force exact search over all 2^n selection
patterns, using the identical feasibility predicates and objective the
Kernel program and the benchmark report both use (scoring.py). Doubles as
a correctness cross-check for the Kernel's own feasible-set filtering --
the two must agree on which patterns are feasible.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from run_selection import N, build_predicate_matrices  # noqa: E402
from scoring import build_candidate_scores, classical_score, is_feasible  # noqa: E402

EXACTLY_SELECTED = 3
DIVERSITY_AT_LEAST = 0.3


def exact_feasible_patterns(
    pairwise: list[list[bool]], diversity: list[list[float]]
) -> list[tuple[int, ...]]:
    return [
        pattern
        for pattern in itertools.product((0, 1), repeat=N)
        if is_feasible(
            pattern,
            pairwise,
            diversity,
            exactly_selected=EXACTLY_SELECTED,
            diversity_at_least=DIVERSITY_AT_LEAST,
        )
    ]


def main() -> int:
    pairwise, diversity = build_predicate_matrices()
    candidate_scores = build_candidate_scores(N)
    feasible = exact_feasible_patterns(pairwise, diversity)
    print(f"feasible patterns: {len(feasible)} / {2 ** N}")
    if not feasible:
        print("no feasible pattern -- baseline cannot rank")
        return 1
    ranked = sorted(
        feasible, key=lambda p: classical_score(p, candidate_scores), reverse=True
    )
    best = ranked[0]
    print(f"best pattern (exact, classical proxy score): {best}")
    print(f"score: {classical_score(best, candidate_scores):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
