"""AT-TDD Phase 1 Red -> Green: `Min` binder for $\\min$, and its
comma-separated `where` guard (matching the equation's own subscript
convention, e.g. $\\min_{i<j:\\,x_ix_j=1}$).

Target: docs/issues/LISS-0428-min-binder.md.
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


def test_min_over_a_single_binding() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        Int m = Min (i In 0..n-1) { n - i }
        Measure m
    }
    """
    result = _run(src)
    assert result.measure.value == 1  # n-i for i=0,1,2 -> 3,2,1


def test_comma_separated_guard_conditions_mean_and() -> None:
    """`where cond1, cond2` -- comma, not `&&`, matching the equation's
    own set-builder/subscript convention. Hand-verified: valid (i,j)
    pairs with i<j and i+j>3 among 0..3 are (1,3)->13 and (2,3)->23."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 4
        Int m = Min (i In 0..n-1, j In 0..n-1) where i < j, i + j > 3 { i * 10 + j }
        Measure m
    }
    """
    result = _run(src)
    assert result.measure.value == 13


def test_min_over_empty_guarded_domain_is_vacuously_satisfied() -> None:
    """LISS-0428 design decision: min over an empty guard-matched domain
    is +infinity (the standard fold identity, matching sum's 0/product's
    1), so a subsequent `>= theta` is vacuously True -- reproducing the
    original `_bind_feasible_predicate`/`scoring.py::is_feasible` Python
    behavior exactly ("if pairs and min(...) < threshold" skips the
    check entirely when no pair is selected)."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        Bool ok = Min (i In 0..n-1, j In 0..n-1) where i < j, i > 100 { 0.0 } >= 5.0
        Measure ok
    }
    """
    result = _run(src)
    assert result.measure.value == True  # noqa: E712


def test_min_target_shape_diversity_threshold_over_state_coordinate() -> None:
    """The exact target shape for S02's `F` predicate's third condition:
    `Min (i In D1, j In D2) where i<j, x[i]*x[j]==1 { D[i][j] } >= theta`
    over a tuple-valued State coordinate. Hand-computed against all 8
    patterns."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        State x = prepare_selection(3)
        Bool ok = Min (i In 0..n-1, j In 0..n-1) where i < j, x[i] * x[j] == 1 { i + j } >= 2
        Measure ok
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    marg = result.measure.marginal
    # D(0,1)=1, D(0,2)=2, D(1,2)=3 (stand-in: i+j). Violated only by 110
    # (selected pair (0,1), D=1<2) and 111 (min(1,2,3)=1<2): 2/8 False.
    assert abs(marg.get(False, 0.0) - 2 / 8) < 1e-9
    assert abs(marg.get(True, 0.0) - 6 / 8) < 1e-9


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0428 Slice B Phase 2 Green")
