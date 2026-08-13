"""AT-TDD Phase 1 Red -> Green: `ForAll` binder for $\\forall$.

Target: docs/issues/LISS-0427-forall-binder.md.
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


def test_forall_true_when_all_elements_satisfy_the_body() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        Bool r = ForAll (i In 0..n-1) { i >= 0 }
        Measure r
    }
    """
    result = _run(src)
    assert result.measure.value == True  # noqa: E712


def test_forall_false_when_one_element_fails() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        Bool r = ForAll (i In 0..n-1) { i < 2 }
        Measure r
    }
    """
    result = _run(src)
    assert result.measure.value == False  # noqa: E712


def test_forall_target_shape_pairwise_implies_over_state_coordinate() -> None:
    """The exact target shape for S02's `F` predicate: `ForAll (i In D1,
    j In D2) where i<j { (x[i]*x[j]==1) Implies (...) }` over a
    tuple-valued State coordinate. Hand-computed against all 8 patterns,
    not just checked to run."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        State x = prepare_selection(3)
        Bool ok = ForAll (i In 0..n-1, j In 0..n-1) where i < j {
            (x[i] * x[j] == 1) Implies (i + j <= 2)
        }
        Measure ok
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    marg = result.measure.marginal
    # compat(0,1)=True, compat(0,2)=True, compat(1,2)=False (1+2=3>2).
    # Violated only by patterns 011 and 111 (pair (1,2) both selected):
    # 2/8 False, 6/8 True.
    assert abs(marg.get(False, 0.0) - 2 / 8) < 1e-9
    assert abs(marg.get(True, 0.0) - 6 / 8) < 1e-9


def test_pi_over_set_power_domain_no_longer_silently_becomes_a_ket_sum() -> None:
    """LISS-0427 correctness fix found while wiring ForAll: `_op_binder`'s
    `{0,1}^n` dispatch previously ignored `kind` entirely, so even `Pi (x
    In {0,1}^n) {...}` would have silently become a `KetSumBinder` (which
    always sums, never products, and doesn't even record `kind`). Now
    only `Sigma` gets that treatment; other kinds fall through to the
    general `OpBinder` path, which correctly rejects a `{0,1}^n` domain
    (out of scope -- classical Sigma/Pi/ForAll only support bare ranges)
    instead of silently mis-evaluating."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Int total = Pi (x In {0,1}^n) { 1 }
        Measure total
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    try:
        Evaluator(seed=0).run_unit(compiled.unit)
        raise AssertionError("expected KernelError for non-Sigma {0,1}^n domain")
    except Exception as e:  # noqa: BLE001
        assert "bare-range binder domain" in str(e)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0427 Slice B Phase 2 Green")
