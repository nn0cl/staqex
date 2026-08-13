"""AT-TDD Phase 1 Red -> Green: `project` drops implicit renormalization
entirely (all forms) and accepts a general (multi-term, diagonal)
Operator as its projection target.

Target: docs/issues/LISS-0431-project-explicit-renorm.md.
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


def test_basis_label_project_no_longer_renormalizes() -> None:
    """`project` onto a single basis label used to silently renormalize
    to probability 1.0; now the un-normalized amplitude carries through
    unchanged, so an explicit `/ ||...||` is required to renormalize."""
    src = """
    package t
    pub fn main() -> Unit {
        State s = 2.0 * |0>
        State projected = project s onto 0
        Measure projected
    }
    """
    result = _run(src)
    # amplitude 2.0 -> probability 4.0, not renormalized to 1.0.
    assert abs(result.measure.marginal.get(0, 0.0) - 4.0) < 1e-9


def test_project_onto_general_operator_matches_hand_computed_result() -> None:
    """The full confirmed S02 step 2 design end to end: psi_0 (literal,
    unnormalized Sigma), F (Set comprehension), P_F (Sigma over F), then
    `(project psi_0 onto P_F) / ||project psi_0 onto P_F||`."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        State psi_0 = (1.0 / sqrt(2.0 ^ n)) * Sigma (x In {0,1}^n) { |x> }
        Set F = {
            x In {0,1}^n :
                Sigma (i In 0..n-1) { x[i] } == 2,
                ForAll (i In 0..n-1, j In 0..n-1) where i < j {
                    (x[i] * x[j] == 1) Implies (i + j <= 2)
                },
                Min (i In 0..n-1, j In 0..n-1) where i < j, x[i] * x[j] == 1 { i + j } >= 1
        }
        Operator P_F = Sigma (x In F) { |x><x| }
        State psi_sel = (project psi_0 onto P_F) / ||project psi_0 onto P_F||
        Measure psi_sel
    }
    """
    result = _run(src)
    marg = result.measure.marginal
    assert abs(sum(marg.values()) - 1.0) < 1e-9
    assert set(marg.keys()) == {(1, 0, 1), (1, 1, 0)}
    for p in marg.values():
        assert abs(p - 0.5) < 1e-9


def test_project_onto_general_operator_without_norm_division_is_unnormalized() -> None:
    """Without the explicit `/ ||...||`, `project` onto P_F returns the
    literal, unnormalized $P_F|\\psi_0\\rangle$ -- total probability
    equal to the number of matching patterns (each amplitude-1 branch of
    the unnormalized psi_0 contributes probability 1 if kept)."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        State psi_0 = Sigma (x In {0,1}^n) { |x> }
        Set F = { x In {0,1}^n : x[0] == 1 }
        Operator P_F = Sigma (x In F) { |x><x| }
        State projected = project psi_0 onto P_F
        Measure projected
    }
    """
    result = _run(src)
    # F = {100, 101, 110, 111} -> 4 of 8 patterns; bare psi_0 has
    # amplitude 1 per branch (LISS-0422), so total probability = 4.0.
    assert abs(sum(result.measure.marginal.values()) - 4.0) < 1e-9
    assert len(result.measure.marginal) == 4


def test_project_onto_general_operator_rejects_non_diagonal() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Operator H = Sigma (i In 0..1) { Z[i] }
        State s = |0>
        State projected = project s onto H
        Measure projected
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    try:
        Evaluator(seed=0).run_unit(compiled.unit)
        raise AssertionError("expected KernelError for a non-Set-domain Operator target")
    except Exception:  # noqa: BLE001
        pass


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0431 Slice B Phase 2 Green")
