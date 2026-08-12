"""AT-TDD: LISS-0133 accepted-surface expression residuals."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_path, compile_source  # noqa: E402


def _hard(source: str) -> list[dict]:
    return [
        d
        for d in compile_source(source).diagnostics
        if not str(d.get("code", "")).startswith("QSEM_")
    ]


def test_float_function_return_binds_as_classical() -> None:
    diags = _hard(
        """
        package t
        pub fn mark() -> Float { return 0.5 }
        pub fn main() -> Unit {
            Float a = mark()
            state x = dirac(0)
            measure x
        }
        """
    )
    assert not any(d.get("code") == "RETURN_TYPE_MISMATCH" for d in diags), diags


def test_delta_time_evolve_for_is_classical() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            state x = |0>
            Delta<Time> dt = 0.1.s
            state x = evolve { x under X for dt }.run()
            measure x
        }
        """
    )
    hard = [d for d in compiled.diagnostics if not str(d.get("code", "")).startswith("QSEM_")]
    assert not any(d.get("code") == "LINEAR_IMPLICIT_DISCARD" for d in hard), hard
    assert compiled.ok or not hard, hard


def test_consume_on_return_product_chain() -> None:
    hard = _hard(
        """
        package t
        pub fn step(c: State<Coin>, x: State<Position>) -> State<(Coin, Position)> {
            return apply(X, c) *|* x
        }
        pub fn main() -> Unit {
            state c = |0>
            state x = dirac(0)
            state s = step(c, x)
            measure s
        }
        """
    )
    assert not any(d.get("code") == "LINEAR_IMPLICIT_DISCARD" for d in hard), hard


def test_multi_register_qualified_site_no_false_positive() -> None:
    compiled = compile_path(
        "examples/basics/B15_multi_register/main_multi_register.sqx"
    )
    multi = [d for d in compiled.diagnostics if d.get("code") == "MULTI_REGISTER_INDEX_AMBIGUOUS"]
    assert multi == [], multi
    hard = [d for d in compiled.diagnostics if not str(d.get("code", "")).startswith("QSEM_")]
    assert compiled.ok or not hard, hard


def test_classical_quantity_scales_state() -> None:
    hard = _hard(
        """
        package t
        pub fn main() -> Unit {
            state bit = coin()
            Time dt = 0.5.s
            Mass m = 1.0.kg
            Stiffness k = 1.0.N_m
            State<Length> x = mix (bit) { 0 -> 0.0.m, else -> 1.0.m }
            State<Momentum> p = mix (bit) { 0 -> 1.0.kg_m_s, else -> 0.0.kg_m_s }
            state (x, p) = evolve (x, p) times 2 {
                (x + (dt / m) * p, p - (dt * k) * x)
            }
            state bit = vacuum
            state p = vacuum
            measure x
        }
        """
    )
    assert not any(
        d.get("code") in {"TYPE_MISMATCH", "EXPECT_CLASSICAL_ONLY_ERROR", "DIMENSION_MISMATCH_ERROR"}
        for d in hard
    ), hard


if __name__ == "__main__":
    test_float_function_return_binds_as_classical()
    test_delta_time_evolve_for_is_classical()
    test_consume_on_return_product_chain()
    test_multi_register_qualified_site_no_false_positive()
    test_classical_quantity_scales_state()
    print("OK — expression residuals")
