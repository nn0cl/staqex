"""AT-TDD: LISS-0144 ND Float[N][M]… coefficient tensors."""

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


def test_2d_float_tensor_lowers_in_binder() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Float[2][2] h = [
            [1.0, 0.0],
            [0.0, 0.5],
        ]
        Operator H = sum (p in Index<0..1>, q in Index<0..1>) {
            h[p][q] * Z[p] * Z[q]
        }
        State a = |0>
        measure a
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    assert "BINDER_LOWERING_UNSUPPORTED" not in codes, codes
    assert "TYPE_MISMATCH" not in codes, codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, diags = lower_finite_binder_operators(compiled.unit)
    assert not diags, diags
    assert "H" in lowered


def test_4d_float_tensor_smoke() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Float[1][1][1][1] v = [[[[2.0]]]]
        Operator H = sum (i in Index<0..0>, j in Index<0..0>, k in Index<0..0>, l in Index<0..0>) {
            v[i][j][k][l] * Z[0]
        }
        State a = |0>
        measure a
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    assert "BINDER_LOWERING_UNSUPPORTED" not in codes, codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, _ = lower_finite_binder_operators(compiled.unit)
    assert "H" in lowered


def test_shape_mismatch_is_diagnosed() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Float[2][2] h = [[1.0], [0.0, 0.5]]
            measure h
        }
        """
    )
    assert "TYPE_MISMATCH" in codes


def test_partial_index_arity_is_rejected() -> None:
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


def test_1d_float_array_still_works() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Float[1] J = [1.0]
        Operator H = sum (i in Index<0..0>) {
            J[i] * Z[i] * Z[next(i)]
        }
        State a = |0>
        measure a
    }
    """
    codes = _codes(source)
    assert "BINDER_LOWERING_UNSUPPORTED" not in codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, _ = lower_finite_binder_operators(compiled.unit)
    assert "H" in lowered


if __name__ == "__main__":
    test_2d_float_tensor_lowers_in_binder()
    print("PASS test_2d_float_tensor_lowers_in_binder")
    test_4d_float_tensor_smoke()
    print("PASS test_4d_float_tensor_smoke")
    test_shape_mismatch_is_diagnosed()
    print("PASS test_shape_mismatch_is_diagnosed")
    test_partial_index_arity_is_rejected()
    print("PASS test_partial_index_arity_is_rejected")
    test_1d_float_array_still_works()
    print("PASS test_1d_float_array_still_works")
