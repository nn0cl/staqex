"""AT-TDD: LISS-0146 dependent / static Index endpoints (ADR 0117)."""

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


def test_register_size_endpoint_lowers() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = Sigma (i In Index<0..register-1>) {
            Z[i]
        }
        State a = |0>
        Measure a
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    assert "BINDER_DOMAIN_ERROR" not in codes, codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, _ = lower_finite_binder_operators(compiled.unit)
    assert "H" in lowered


def test_dependent_inner_range_lowers() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = Sigma (i In Index<0..register-1>, j In Index<i+1..register-1>) {
            Z[i] * Z[j]
        }
        State a = |0>
        Measure a
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, _ = lower_finite_binder_operators(compiled.unit)
    assert "H" in lowered


def test_negative_endpoint_is_diagnosed() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<2> register = system()
            Operator H = Sigma (i In Index<0..0-1>) { Z[0] }
            State a = |0>
            Measure a
        }
        """
    )
    assert "BINDER_DOMAIN_ERROR" in codes


if __name__ == "__main__":
    test_register_size_endpoint_lowers()
    print("PASS test_register_size_endpoint_lowers")
    test_dependent_inner_range_lowers()
    print("PASS test_dependent_inner_range_lowers")
    test_negative_endpoint_is_diagnosed()
    print("PASS test_negative_endpoint_is_diagnosed")
