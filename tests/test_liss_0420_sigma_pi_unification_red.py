"""AT-TDD Phase 1 Red -> Green: unify `sum`/`product` into `Sigma`/`Pi`,
with new State-typed ket-sum body support.

Target: docs/issues/LISS-0420-sigma-pi-unification.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_ket_sum_over_bit_domain_is_equal_superposition() -> None:
    """`Sigma (x In {0,1}^n) { |x> }` alone is self-normalizing, matching
    `prepare_selection(n)` exactly (same equal-weight construction)."""
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
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    total = sum(result.measure.marginal.values())
    assert abs(total - 1.0) < 1e-9
    assert len(result.measure.marginal) == 16
    for p in result.measure.marginal.values():
        assert abs(p - 1.0 / 16) < 1e-9


def test_ket_sum_matches_prepare_selection_exactly() -> None:
    src_sigma = """
    package t
    pub fn main() -> Unit {
        Int n = 6
        State psi = Sigma (x In {0,1}^n) { |x> }
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
    r1 = Evaluator(seed=0).run_unit(c1.unit)
    r2 = Evaluator(seed=0).run_unit(c2.unit)
    assert r1.measure.marginal == r2.measure.marginal


def test_external_coefficient_applies_literally_and_can_unnormalize() -> None:
    """LISS-0420 design finding: the Sigma ket-sum is already self-
    normalizing, so an *explicit* external coefficient (matching how the
    equation reads aloud) double-applies -- honest, unnormalized output,
    matching this codebase's established precedent of never silently
    enforcing normalization (LISS-0410: apply() with a non-unitary
    Operator already produced an unnormalized result, not an error)."""
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
    result = Evaluator(seed=0).run_unit(compiled.unit)
    total = sum(result.measure.marginal.values())
    # Self-normalized Sigma (total=1.0) scaled by amplitude coefficient
    # (1/sqrt(2^n)) -- probability scales by the coefficient SQUARED.
    coeff = 1.0 / (2.0**4) ** 0.5
    expected_total = 1.0 * coeff * coeff
    assert abs(total - expected_total) < 1e-9


def test_operator_sigma_binder_still_works_with_In() -> None:
    """Regression guard: the existing Operator-DSL sum/product binder,
    renamed to Sigma/Pi, must still work identically -- now spelled with
    the capitalized `In` domain-membership keyword."""
    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Sigma (i In Index<0..1>) { Z[i] }
        Operator H = scale * H_raw
        State (a, b) = (|0>, |0>)
        State (a, b) = Evolve { (a, b) under H for 0.1.fs }.run()
        Measure a tracing_out b
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None


def test_operator_pi_binder_still_works() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Pi (i In Index<0..1>) { Z[i] }
        Operator H = scale * H_raw
        State (a, b) = (|0>, |0>)
        State (a, b) = Evolve { (a, b) under H for 0.1.fs }.run()
        Measure a tracing_out b
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None


def test_multi_binding_operator_sigma_with_guard_still_works() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Sigma (i In Index<0..2>, j In Index<0..2>) where i < j {
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
    result = Evaluator(seed=0).run_unit(compiled.unit)
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
