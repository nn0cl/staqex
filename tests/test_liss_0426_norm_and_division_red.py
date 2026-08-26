"""AT-TDD Phase 1 Red -> Green: `||State||` norm notation + `State / Float`
division.

Target: docs/issues/LISS-0426-norm-and-state-division.md.
"""

from __future__ import annotations

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
    return Evaluator(seed=0).run_unit(compiled.unit)


def test_norm_of_a_ket_lit_is_one() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State a = |0>
        Float n = ||a||
        Measure n
    }
    """
    result = _run(src)
    assert abs(result.measure.value - 1.0) < 1e-9


def test_norm_of_unnormalized_literal_ket_sum_matches_sqrt_of_total_probability() -> None:
    """`Sigma (x In {0,1}^n) { |x> }` is literally unnormalized (LISS-0422)
    -- its own norm should be `sqrt(2**n)`, not 1."""
    src = """
    package t
    pub fn main() -> Unit {
        State s = Sigma (x In {0,1}^2) { |x> }
        Float n = ||s||
        Measure n
    }
    """
    result = _run(src)
    assert abs(result.measure.value - 2.0) < 1e-9  # sqrt(4)


def test_state_divided_by_its_own_norm_is_a_literal_normalize() -> None:
    """The exact target shape for S02 step 2:
    `X / ||X||` where X is repeated literally (matching the equation's
    own repetition of $P_F|\\psi_0\\rangle$ in numerator and norm)."""
    src = """
    package t
    pub fn main() -> Unit {
        State normalized = (Sigma (x In {0,1}^2) { |x> }) / ||Sigma (x In {0,1}^2) { |x> }||
        Measure normalized
    }
    """
    result = _run(src)
    total = sum(result.measure.marginal.values())
    assert abs(total - 1.0) < 1e-9
    assert len(result.measure.marginal) == 4
    for p in result.measure.marginal.values():
        assert abs(p - 0.25) < 1e-9


def test_binary_or_is_unaffected_by_norm_bars_disambiguation() -> None:
    """`a || b` (logical or) must still parse and evaluate correctly --
    the norm-bars depth counter must not leak into ordinary `||` use."""
    src = """
    package t
    pub fn main() -> Unit {
        Bool a = true
        Bool b = false
        Bool r = a || b
        Measure r
    }
    """
    result = _run(src)
    assert result.measure.value == True  # noqa: E712


def test_norm_requires_a_state_operand() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int x = 3
        Float n = ||x||
        Measure n
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "TYPE_MISMATCH" in codes, compiled.diagnostics


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0426 Slice B Phase 2 Green")
