"""AT-TDD Phase 1 Red: LISS-0055 binder bodies as operator expressions.

These tests describe the accepted physicist-facing surface before the
general binder parser/lowering implementation exists.  They intentionally
assert the desired successful compilation and therefore remain Red until the
Phase 2 implementation is approved.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _main(body: str):
    return compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            {body}
            State observed = |0>
            Measure observed
        }}
        """
    )


def test_binder_body_accepts_sum_of_operator_terms_and_named_coefficient() -> None:
    compiled = _main(
        """
        Float J = 1.0
        Operator H = Sigma (i In Index<0..2>) {
            J * (X[i] * X[next(i)] + Y[i] * Y[next(i)])
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_nested_sum_is_a_valid_operator_expression() -> None:
    compiled = _main(
        """
        Operator H = Sigma (i In Index<0..1>) {
            Sigma (j In Index<0..1>) { Z[i] * Z[j] }
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_multi_variable_sum_head_matches_nested_sum_surface() -> None:
    compiled = _main(
        """
        Operator H = Sigma (
            i In Index<0..1>,
            j In Index<0..1>
        ) { Z[i] * Z[j] }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_where_is_a_static_index_constraint_not_quantum_when() -> None:
    compiled = _main(
        """
        Operator H = Sigma (
            i In Index<0..3>,
            j In Index<0..3>
        ) where i < j {
            Z[i] * Z[j]
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_second_quantized_atoms_can_be_composed_inside_a_binder() -> None:
    compiled = _main(
        """
        Operator H = Sigma (i In Index<0..1>) {
            create[i] * annihilate[i]
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_product_is_lowered_with_a_defined_nonempty_order() -> None:
    compiled = _main(
        """
        Operator H = Pi (i In Index<0..1>) { Z[i] }
        """
    )

    assert compiled.ok, compiled.diagnostics


if __name__ == "__main__":
    tests = [
        test_binder_body_accepts_sum_of_operator_terms_and_named_coefficient,
        test_nested_sum_is_a_valid_operator_expression,
        test_multi_variable_sum_head_matches_nested_sum_surface,
        test_where_is_a_static_index_constraint_not_quantum_when,
        test_second_quantized_atoms_can_be_composed_inside_a_binder,
        test_product_is_lowered_with_a_defined_nonempty_order,
    ]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:  # noqa: BLE001 -- Red run report only
            failed += 1
            print(f"RED (expected): {test.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{passed} passed, {failed} failed (LISS-0055 Phase 1 Red)")

