"""LISS-0270 / ADR 0176: experiment surface profile (short ceremony)."""

from __future__ import annotations

from compiler.staqex.host import run_source
from compiler.staqex.pipeline import compile_source


def test_experiment_profile_omits_package_and_main_wrapper() -> None:
    src = """
// staqex-profile: experiment
Float J = 1.0545718e-19
Float h = 5.272859e-20
Operator H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
state s0 = |+>
state s1 = |+>
state (s0, s1) = evolve { (s0, s1) under H for 0.7.fs using Suzuki(order = 2, steps = 4) }.run()
measure s0 tracing_out s1
"""
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.unit.package is not None
    assert compiled.unit.package.path == ["staqex", "experiment"]
    assert compiled.unit.main is not None

    result = run_source(src, settings={"seed": 0})
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements
    assert not result.measurements[-1].vacuum


def test_without_profile_toplevel_still_errors() -> None:
    # ADR 0182: no-package sources default to experiment profile (no longer error).
    # Packaged sources without main still error (see sugar suite).
    src = """
package demo.requires_main
Float J = 1.0
state s0 = |0>
measure s0
"""
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "TOPLEVEL_EXECUTION_ERROR" in codes


def test_explicit_package_still_valid_with_profile() -> None:
    src = """
// staqex-profile: experiment
package demo.short
pub fn main() -> Unit {
    state s = dirac(1)
    measure s
}
"""
    result = run_source(src, settings={"seed": 0})
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[-1].value == 1
