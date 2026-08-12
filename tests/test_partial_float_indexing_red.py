"""AT-TDD: LISS-0149 partial Float classical indexing (ADR 0118)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_classical_partial_float_bind_then_binder() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Float[2][2] h = [
            [1.0, 0.0],
            [0.0, 0.5],
        ]
        Float[2] row = h[1]
        Operator H = sum (q in Index<0..1>) {
            row[q] * Z[q]
        }
        State a = |0>
        measure a
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    assert "TYPE_MISMATCH" not in codes, codes
    assert "BINDER_LOWERING_UNSUPPORTED" not in codes, codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, diags = lower_finite_binder_operators(compiled.unit)
    assert not diags, diags
    assert "H" in lowered


def test_partial_as_scalar_coeff_still_rejected() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<2> register = system()
            Float[2][2] h = [[1.0, 0.0], [0.0, 0.5]]
            Operator H = sum (p in Index<0..1>) {
                h[p] * Z[p]
            }
            State a = |0>
            measure a
        }
        """
    )
    assert "BINDER_LOWERING_UNSUPPORTED" in codes or "TYPE_MISMATCH" in codes


def test_partial_shape_mismatch_is_diagnosed() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Float[2][3] h = [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
            ]
            Float[2] row = h[0]
            State a = |0>
            measure a
        }
        """
    )
    assert "TYPE_MISMATCH" in codes


if __name__ == "__main__":
    test_classical_partial_float_bind_then_binder()
    print("PASS test_classical_partial_float_bind_then_binder")
    test_partial_as_scalar_coeff_still_rejected()
    print("PASS test_partial_as_scalar_coeff_still_rejected")
    test_partial_shape_mismatch_is_diagnosed()
    print("PASS test_partial_shape_mismatch_is_diagnosed")
