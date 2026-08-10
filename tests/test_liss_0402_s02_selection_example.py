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


def test_main_selection_runs_and_respects_feasibility() -> None:
    pairwise, diversity = _predicate_matrices(8)
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
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements
    envelope = result.measurements[0]
    assert envelope.vacuum is False
    pattern = envelope.value
    assert sum(pattern) == 3
    selected = [i for i, bit in enumerate(pattern) if bit]
    for i in selected:
        for j in selected:
            if i < j:
                assert pairwise[i][j], "selected pair must be pairwise-compatible"
    if len(selected) >= 2:
        import itertools

        min_div = min(
            diversity[i][j] for i, j in itertools.combinations(selected, 2)
        )
        assert min_div >= 0.3


def test_classical_baseline_agrees_on_feasible_set() -> None:
    sys.path.insert(0, str(_HOST_DIR))
    try:
        from run_selection import N, build_predicate_matrices
        from classical_baseline import is_feasible

        pairwise, diversity = build_predicate_matrices()
        feasible = [
            p
            for p in __import__("itertools").product((0, 1), repeat=N)
            if is_feasible(p, pairwise, diversity)
        ]
        assert feasible, "baseline must find at least one feasible pattern"
    finally:
        sys.path.remove(str(_HOST_DIR))
