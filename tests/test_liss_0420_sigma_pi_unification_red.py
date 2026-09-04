"""AT-TDD Phase 1 Red -> Green: unify `sum`/`product` into `Sigma`/`Pi`,
with new State-typed ket-sum body support.

Target: docs/issues/LISS-0420-sigma-pi-unification.md.
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


def test_bare_ket_sum_is_literal_and_unnormalized() -> None:
    """LISS-0422: `Sigma (x In {0,1}^n) { |x> }` alone is the literal,
    UNNORMALIZED sum $\\sum_x |x\\rangle$ -- each basis ket gets amplitude
    1, exactly matching the bare blackboard `Sigma` symbol (which never
    carries implicit normalization; the blackboard equation's own
    `1/sqrt(2^n)` prefactor is a separate, explicit factor). Total
    probability is therefore `2**n`, not 1."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 4
        State psi = Sigma (x In {0,1}^n) { |x> }
        Measure psi
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None
    total = sum(result.measure.marginal.values())
    assert abs(total - 16.0) < 1e-9
    assert len(result.measure.marginal) == 16
    for p in result.measure.marginal.values():
        assert abs(p - 1.0) < 1e-9


def test_coefficient_scaled_ket_sum_matches_prepare_selection_exactly() -> None:
    """The literal blackboard transcription -- Sigma (unnormalized) times
    the explicit `1/sqrt(2^n)` coefficient -- reproduces
    `prepare_selection(n)`'s normalized equal superposition exactly.
    Bare `Sigma` alone no longer matches `prepare_selection` (LISS-0422
    correction); only the fully-transcribed equation does."""
    src_sigma = """
    package t
    pub fn main() -> Unit {
        Int n = 6
        State psi = (1.0 / sqrt(2.0 ^ n)) * Sigma (x In {0,1}^n) { |x> }
        Measure psi
    }
    """
    src_prepare = """
    package t
    pub fn main() -> Unit {
        State psi = prepare_selection(6)
        Measure psi
    }
    """
    c1 = compile_source(src_sigma)
    c2 = compile_source(src_prepare)
    assert c1.unit is not None, c1.diagnostics
    assert c2.unit is not None, c2.diagnostics
    r1 = run_canonical(c1, Evaluator(seed=0))
    r2 = run_canonical(c2, Evaluator(seed=0))
    assert r1.measure.marginal == r2.measure.marginal


def test_external_coefficient_applies_literally_as_amplitude_scale() -> None:
    """LISS-0422: the external coefficient multiplies each branch's
    amplitude directly (`amp *= scale`); since bare Sigma now has
    amplitude 1 per branch (not sqrt(1/N)), a coefficient of
    `1/sqrt(2^n)` yields probability `1/2^n` per branch, i.e. total
    probability 1.0 -- the coefficient is REQUIRED for normalization,
    not optional/redundant (correcting LISS-0420's original,
    self-normalizing-Sigma framing)."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 4
        State psi = (1.0 / sqrt(2.0 ^ n)) * Sigma (x In {0,1}^n) { |x> }
        Measure psi
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    total = sum(result.measure.marginal.values())
    assert abs(total - 1.0) < 1e-9
    for p in result.measure.marginal.values():
        assert abs(p - 1.0 / 16.0) < 1e-9


def test_operator_sigma_binder_still_works_with_In() -> None:
    """Regression guard: the existing Operator-DSL sum/product binder,
    renamed to Sigma/Pi, must still work identically -- now spelled with
    the capitalized `In` domain-membership keyword."""
    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Sigma (i In 0..1) { Z[i] }
        Operator H = scale * H_raw
        State (a, b) = (|0>, |0>)
        State (a, b) = Evolve { (a, b) under H for 0.1.fs }.run()
        Measure a tracing_out b
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None


def test_operator_pi_binder_still_works() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Pi (i In 0..1) { Z[i] }
        Operator H = scale * H_raw
        State (a, b) = (|0>, |0>)
        State (a, b) = Evolve { (a, b) under H for 0.1.fs }.run()
        Measure a tracing_out b
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None


def test_multi_binding_operator_sigma_with_guard_still_works() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Sigma (i In 0..2, j In 0..2) where i < j {
            Z[i] * Z[j]
        }
        Operator H = scale * H_raw
        State (a, b, c) = (|0>, |0>, |0>)
        State (a, b, c) = Evolve { (a, b, c) under H for 0.1.fs using Suzuki(order = 2, steps = 2) }.run()
        Measure a tracing_out b, c
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None


def test_lowercase_sum_product_are_no_longer_binders() -> None:
    """`sum`/`product` were never reserved keywords (contextual, name-
    based recognition only inside the Operator-DSL) -- they simply stop
    being recognized as the binder shape; using them there now fails to
    parse as Operator-DSL (falls through to a generic classical
    expression / undefined-name path), not a special retirement
    diagnostic."""
    src = """
    package t
    pub fn main() -> Unit {
        Operator H = sum (i in Index<0..1>) { Z[i] }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "PARSE_ERROR" in codes, compiled.diagnostics


def test_ket_sum_body_must_reference_the_bound_variable() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 4
        State psi = Sigma (x In {0,1}^n) { |y> }
        Measure psi
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "PARSE_ERROR" in codes, compiled.diagnostics
