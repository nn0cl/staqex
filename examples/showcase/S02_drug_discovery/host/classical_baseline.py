#!/usr/bin/env python3
"""Classical baseline for main_selection.sqx (LISS-0402, design doc §7
"Baseline discipline"): brute-force exact search over all 2^n selection
patterns, using the identical feasibility predicates and objective the
Kernel program uses. Doubles as a correctness cross-check for the
Kernel's own feasible-set filtering -- the two must agree on which
patterns are feasible.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from run_selection import N, build_predicate_matrices  # noqa: E402

EXACTLY_SELECTED = 3
DIVERSITY_AT_LEAST = 0.3

# Mirrors main_selection.sqx's ObjectiveWeights + objective_hamiltonian
# reading (Z -> +1/-1 per bit, X term has no classical diagonal analogue so
# it is omitted from this classical proxy score; ZZ pairwise term uses the
# product of the two bits' +1/-1 values). This is a classical proxy for
# ranking feasible patterns, not a re-derivation of the quantum expectation
# value -- the two are not required to numerically match, only to agree on
# the *feasible set* itself.
ACTIVITY_WEIGHT = 0.45
DIVERSITY_WEIGHT = 0.20


def is_feasible(
    pattern: tuple[int, ...],
    pairwise: list[list[bool]],
    diversity: list[list[float]],
) -> bool:
    if sum(pattern) != EXACTLY_SELECTED:
        return False
    selected = [i for i, bit in enumerate(pattern) if bit]
    for i, j in itertools.combinations(selected, 2):
        if not pairwise[i][j]:
            return False
    pairs = list(itertools.combinations(selected, 2))
    if pairs and min(diversity[i][j] for i, j in pairs) < DIVERSITY_AT_LEAST:
        return False
    return True


def classical_score(pattern: tuple[int, ...]) -> float:
    spins = [1 if bit else -1 for bit in pattern]
    activity = sum(spins) * ACTIVITY_WEIGHT
    diversity = sum(
        spins[i] * spins[j] for i, j in itertools.combinations(range(len(pattern)), 2)
    ) * DIVERSITY_WEIGHT
    return activity + diversity


def main() -> int:
    pairwise, diversity = build_predicate_matrices()
    feasible = [
        pattern
        for pattern in itertools.product((0, 1), repeat=N)
        if is_feasible(pattern, pairwise, diversity)
    ]
    print(f"feasible patterns: {len(feasible)} / {2 ** N}")
    if not feasible:
        print("no feasible pattern -- baseline cannot rank")
        return 1
    ranked = sorted(feasible, key=classical_score, reverse=True)
    best = ranked[0]
    print(f"best pattern (exact, classical proxy score): {best}")
    print(f"score: {classical_score(best):.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
