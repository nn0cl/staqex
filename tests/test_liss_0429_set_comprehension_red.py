"""AT-TDD Phase 1 Red -> Green: `Set F = { x In D : cond1, cond2, ... }`
comprehension.

Target: docs/issues/LISS-0429-set-comprehension.md.
"""

from __future__ import annotations

from canonical_execution import run_canonical

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def _run(src: str):
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    return run_canonical(compiled, Evaluator(seed=0))


def test_single_condition_filters_the_set_power_domain() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Set F = { x In {0,1}^n : x[0] == 1 }
        Measure F
    }
    """
    result = _run(src)
    assert set(result.measure.value) == {(1, 0), (1, 1)}


def test_comma_separated_conditions_mean_and() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Set F = { x In {0,1}^n : x[0] == 1, x[1] == 1 }
        Measure F
    }
    """
    result = _run(src)
    assert set(result.measure.value) == {(1, 1)}


def test_target_shape_all_three_s02_f_conditions_together() -> None:
    """The confirmed final design for S02's `F`: exactly-2-selected
    (classical Sigma) + pairwise Implies (ForAll) + diversity threshold
    (Min), all as comma-separated conditions in one comprehension. Hand-
    verified against all 8 patterns of n=3, not just checked to run."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        Set F = {
            x In {0,1}^n :
                Sigma (i In 0..n-1) { x[i] } == 2,
                ForAll (i In 0..n-1, j In 0..n-1) where i < j {
                    (x[i] * x[j] == 1) Implies (i + j <= 2)
                },
                Min (i In 0..n-1, j In 0..n-1) where i < j, x[i] * x[j] == 1 { i + j } >= 1
        }
        Measure F
    }
    """
    result = _run(src)
    # Exactly-2 patterns: 011, 101, 110. Pairwise (i+j<=2 when both
    # selected) excludes 011 (pair (1,2), sum 3). Diversity (min i+j >= 1
    # over selected pairs) excludes nothing further here.
    assert set(result.measure.value) == {(1, 0, 1), (1, 1, 0)}


def test_empty_result_when_no_element_satisfies_all_conditions() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Set F = { x In {0,1}^n : x[0] == 1, x[0] == 0 }
        Measure F
    }
    """
    result = _run(src)
    assert result.measure.value == ()


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0429 Slice B Phase 2 Green")
