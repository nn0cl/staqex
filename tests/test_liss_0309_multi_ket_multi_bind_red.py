"""LISS-0309: multi-ket multi-bind is a live linear pair."""

from __future__ import annotations

from compiler.staqex.host import run_source


def test_multi_ket_multi_bind_measure_tracing_out() -> None:
    src = """
// staqex-lane: experiment
s0, s1 = |+>, |+>
measure s0 tracing_out s1
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_ideal_dialect_multi_bind_chalk() -> None:
    """Classical multi-bind + multi-ket + evolve (minimal dialect sketch)."""
    src = """
// staqex-lane: experiment
J, h = 1.0545718e-19, 5.272859e-20
H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
s0, s1 = |+>, |+>
state (s0, s1) = evolve { (s0, s1) under H for 0.7.fs using Suzuki(order = 2, steps = 6) }.run()
measure s0 tracing_out s1
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_classical_multi_bind_not_linearized() -> None:
    """Classical multi-bind must not create linear discard obligations."""
    src = """
// staqex-lane: experiment
a, b = 1.0, 2.0
state s = dirac(a + b)
measure s
"""
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == 3.0
