#!/usr/bin/env python3
"""Run main_selection.sqx with its required HostInputPort data (LISS-0402).

pairwise_compatible / diversity_at_least matrices are Host-computed
classical data (ADR 0194) -- the Kernel never sees candidate identity,
only the finite width n and the terminal selection pattern.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import submit_path  # noqa: E402

_SQX = Path(__file__).resolve().parents[1] / "main_selection.sqx"

N = 8


def build_predicate_matrices() -> tuple[list[list[bool]], list[list[float]]]:
    """Toy synthetic fixture: candidates 0/1 are incompatible (e.g. same
    binding pocket); diversity scores fall off with candidate-index
    distance (toy proxy for structural similarity)."""
    pairwise = [[True] * N for _ in range(N)]
    pairwise[0][1] = pairwise[1][0] = False
    diversity = [
        [max(0.0, 1.0 - 0.15 * abs(i - j)) for j in range(N)] for i in range(N)
    ]
    return pairwise, diversity


def main() -> int:
    pairwise, diversity = build_predicate_matrices()
    job = submit_path(
        str(_SQX),
        settings={
            "seed": 0,
            "inputs": {
                "pairwise_compatible": pairwise,
                "diversity_at_least": diversity,
            },
        },
    )
    result = job.result()
    print(f"status: {result.status}")
    if result.measurements:
        envelope = result.measurements[0]
        print(f"selection pattern: {envelope.value}")
        print(f"vacuum: {envelope.vacuum}")
    else:
        print("no terminal measurement")
    return 0 if result.status == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
