"""LISS-0273 / ADR 0179: pure classical Call as expression operand."""

from __future__ import annotations

from compiler.staqex.host import run_source


def test_classical_method_times_literal_in_expr() -> None:
    src = """
package p
namespace N {
    pub class C {
        pub val v: Float
        fn init(v: Float) { this.v = v }
        pub fn get() -> Float { return this.v }
    }
}
pub fn main() -> Unit {
    N.C c = N.C(2.0)
    Float b = c.get() * 0.4
    State x = Dirac(b)
    Measure x
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements
    assert r.measurements[-1].value == 0.8


def test_classical_free_fn_in_binop() -> None:
    src = """
package p
fn twice(x: Float) -> Float {
    return x + x
}
pub fn main() -> Unit {
    Float y = twice(1.5) + 0.5
    State x = Dirac(y)
    Measure x
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 3.5


def test_state_forming_call_still_not_classical_operand() -> None:
    src = """
package p
pub fn main() -> Unit {
    Float bad = Coin() * 0.5
    State x = Dirac(0)
    Measure x
}
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "failed"
    codes = " ".join(str(d.get("message", "")) + str(d.get("code", "")) for d in r.diagnostics)
    assert "Coin" in codes.lower() or "classical" in codes.lower() or "RUNTIME" in codes
