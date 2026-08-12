"""Regression guard: the sparse-evolution step-budget overflow error
names the actionable fix (ADR 0195's `Energy scale = ...to J` idiom),
not just the bare magnitude -- a real discoverability gap found while
writing S02 (LISS-0402/0406), fixed without changing when the error
fires.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelError  # noqa: E402


def test_evolve_overflow_error_names_the_energy_scale_fix() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Operator H = 1.0 * Z[0]
        state q = |0>
        Time dur = 1.0.fs
        state q = evolve { q under H for dur }.run()
        measure q
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    raised = None
    try:
        Evaluator(seed=0).run_unit(compiled.unit)
    except KernelError as exc:
        raised = exc
    assert raised is not None, "expected the evolution step budget to overflow"
    message = str(raised)
    assert "ADR 0195" in message
    assert "Energy scale" in message
    assert ".eV to J" in message
