"""AT-TDD Phase 1 Red: LISS-0030 mathematical binders.

The syntax and diagnostics here are the reviewed acceptance boundary. The
current Kernel intentionally does not implement symbolic binders yet.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_finite_sum_is_a_typed_formula_expression() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Dimension sites = 4
            Operator H = Sigma (i In sites) { Z[i] * Z[next(i)] }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_product_is_not_an_imperative_runtime_loop() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Operator H = Pi (i In 0..4-1) {
                log(i)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "MATHEMATICAL_BINDER_EFFECT_ERROR" in codes


def test_binder_rejects_execution_count_as_a_theory_domain() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            ShotCount shots = 1000
            Operator H = Sigma (i In shots) { Z[i] }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "PHASE_TYPE_VISIBILITY_ERROR" in codes


def test_binder_preserves_source_when_expansion_budget_is_exceeded() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Dimension sites = 1000000000
            Operator H = Sigma (i In sites) { Z[i] }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "BINDER_RESOURCE_ERROR" in codes


def test_empty_or_zero_dimension_domain_is_rejected() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Dimension sites = 0
            Operator H = Sigma (i In sites) { Z[i] }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "BINDER_DOMAIN_ERROR" in codes


def test_index_type_domain_requires_positive_finite_shape() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Operator H = Sigma (i In 0..0-1) { Z[i] }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "BINDER_DOMAIN_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_finite_sum_is_a_typed_formula_expression,
        test_product_is_not_an_imperative_runtime_loop,
        test_binder_rejects_execution_count_as_a_theory_domain,
        test_binder_preserves_source_when_expansion_budget_is_exceeded,
        test_empty_or_zero_dimension_domain_is_rejected,
        test_index_type_domain_requires_positive_finite_shape,
    ):
        test()
    print("OK — mathematical binder tests")
