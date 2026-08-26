"""LISS-0305 / ADR 0184: classical multi-name bind."""

from __future__ import annotations

from compiler.staqex.host import run_source
from compiler.staqex.pipeline import HARD_CODES, compile_source


def test_classical_multi_bind_operator_coeffs() -> None:
    src = """
// staqex-lane: experiment
J, h = 1.0545718e-19, 5.272859e-20
H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
State s0 = |+>
State s1 = |+>
State (s0, s1) = Evolve { (s0, s1) under H for 0.7.fs using Suzuki(order = 2, steps = 6) }.run()
Measure s0 tracing_out s1
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_multi_bind_arity_mismatch_parse_hard() -> None:
    src = """
// staqex-lane: experiment
J, h = 1.0
State s = |0>
Measure s
"""
    c = compile_source(src)
    assert any(d.get("code") in HARD_CODES for d in c.diagnostics) or any(
        d.get("code") == "PARSE_ERROR" for d in c.diagnostics
    )


def test_three_name_classical_multi_bind() -> None:
    src = """
// staqex-lane: experiment
a, b, c = 1.0, 2.0, 3.0
State s = Dirac(a + b + c)
Measure s
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 6.0
