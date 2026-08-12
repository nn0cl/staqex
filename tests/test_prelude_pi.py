"""ADR 0062 — prelude classical constants `pi`, `sqrt2`, `inv_sqrt2`."""

from __future__ import annotations

import io
import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.stdlib.prelude import PRELUDE_CONSTANTS, is_prelude  # noqa: E402


def test_prelude_exports_pi() -> None:
    assert is_prelude("pi")
    assert abs(PRELUDE_CONSTANTS["pi"] - math.pi) < 1e-15


def test_prelude_exports_inv_sqrt2() -> None:
    assert is_prelude("inv_sqrt2")
    assert is_prelude("sqrt2")
    assert abs(PRELUDE_CONSTANTS["inv_sqrt2"] - 1.0 / math.sqrt(2.0)) < 1e-15
    assert abs(PRELUDE_CONSTANTS["sqrt2"] - math.sqrt(2.0)) < 1e-15
    assert abs(PRELUDE_CONSTANTS["inv_sqrt2"] * PRELUDE_CONSTANTS["sqrt2"] - 1.0) < 1e-15


def test_phase_with_pi_matches_literal() -> None:
    src_pi = """
package t
pub fn main() -> Unit {
    State b0 = coin()
    State b1 = coin()
    State idx = b0 * 2 + b1
    State b0 = |0>
    State b1 = |0>
    State marked = phase(idx, pi, 2)
    State amplified = grover_diffuse(marked)
    measure amplified
}
"""
    src_lit = """
package t
pub fn main() -> Unit {
    State b0 = coin()
    State b1 = coin()
    State idx = b0 * 2 + b1
    State b0 = |0>
    State b1 = |0>
    State marked = phase(idx, 3.141592653589793, 2)
    State amplified = grover_diffuse(marked)
    measure amplified
}
"""
    a = run_source(src_pi, seed=0, stdout=io.StringIO())
    b = run_source(src_lit, seed=0, stdout=io.StringIO())
    assert a.compile_ok and b.compile_ok
    assert a.eval.measure is not None and b.eval.measure is not None
    assert a.eval.measure.value == b.eval.measure.value == 2


def test_pi_half_in_phase() -> None:
    src = """
package t
pub fn main() -> Unit {
    State z = |0>
    State zp = phase(z, pi / 2.0)
    State viewed = inspect(zp)
    measure viewed
}
"""
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics


def test_math_pi_alias_matches_pi() -> None:
    src = """
package t
pub fn main() -> Unit {
    State b0 = coin()
    State b1 = coin()
    State idx = b0 * 2 + b1
    State b0 = |0>
    State b1 = |0>
    State marked = phase(idx, Math.pi, 2)
    State amplified = grover_diffuse(marked)
    measure amplified
}
"""
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics
    assert r.eval.measure is not None
    assert r.eval.measure.value == 2


def test_hadamard_coin_via_inv_sqrt2() -> None:
    src = """
package t
pub fn main() -> Unit {
    Operator Coin = (X + Z) * inv_sqrt2
    State q = |0>
    State q = apply(Coin, q)
    State viewed = inspect(q)
    measure viewed
}
"""
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics


def test_math_inv_sqrt2_alias() -> None:
    src = """
package t
pub fn main() -> Unit {
    Float s = Math.inv_sqrt2
    Operator Coin = (X + Z) * s
    State q = |0>
    State q = apply(Coin, q)
    measure q
}
"""
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics


def test_state_plus_pi_type_error() -> None:
    src = """
package t
pub fn main() -> Unit {
    State psi = |0>
    State bad = psi + pi
    measure bad
}
"""
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "TYPE_MISMATCH" in codes or "EXPECT_CLASSICAL_ONLY_ERROR" in codes


if __name__ == "__main__":
    test_prelude_exports_pi()
    test_prelude_exports_inv_sqrt2()
    test_phase_with_pi_matches_literal()
    test_pi_half_in_phase()
    test_math_pi_alias_matches_pi()
    test_hadamard_coin_via_inv_sqrt2()
    test_math_inv_sqrt2_alias()
    test_state_plus_pi_type_error()
    print("OK — prelude constants")
