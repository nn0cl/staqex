"""AT-TDD: LISS-0373 -- a `where` binder guard accepts the same
next(...)/wrap(...) index-accessor shapes an indexed operator body
already does (was an UNCAUGHT ValueError crashing compile_source()
itself, the most severe finding this session -- not a diagnostic, a
raw exception from the public compiler API).

Design decision: docs/issues/LISS-0373-where-guard-accessor-crash.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402
from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402


def _src(hamiltonian: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        QubitRegister<3> register = system()
        Operator H = {hamiltonian}
        state a = |0>
        state b = |0>
        state c = |0>
        state (a, b, c) = evolve {{ (a, b, c) under H for 0.1 using Suzuki(order = 2, steps = 1) }}.run()
        state b = |0>
        state c = |0>
        measure a
    }}
    """


_NEXT_GUARD_SRC = _src(
    "sum (i in Index<0..2>, j in Index<0..2>) where i == next(j) { Z[i] * Z[j] }"
)


def test_next_accessor_in_where_guard_does_not_crash_the_compiler() -> None:
    """Regression guard: compile_source() must never raise for this
    source -- it must return a CompileResult, ok or not."""
    compiled = compile_source(_NEXT_GUARD_SRC)
    assert compiled.ok, compiled.diagnostics


def test_next_accessor_guard_matches_the_equivalent_hand_written_hamiltonian() -> None:
    """`where i == next(j)` over Index<0..2>x Index<0..2> should retain
    exactly the (i, j) = (1, 0) and (2, 1) terms -- the same Hamiltonian
    as writing Z[1]*Z[0] + Z[2]*Z[1] directly."""
    manual_src = _src("Z[1] * Z[0] + Z[2] * Z[1]")

    guard_compiled = compile_source(_NEXT_GUARD_SRC)
    assert guard_compiled.ok, guard_compiled.diagnostics
    guard_emitted = QASM3Emitter(route=False).emit_unit(guard_compiled.unit)
    assert guard_emitted.ok, guard_emitted.notes

    manual_compiled = compile_source(manual_src)
    assert manual_compiled.ok, manual_compiled.diagnostics
    manual_emitted = QASM3Emitter(route=False).emit_unit(manual_compiled.unit)
    assert manual_emitted.ok, manual_emitted.notes

    assert guard_emitted.qasm.count("rz(") == manual_emitted.qasm.count("rz(")
    assert guard_emitted.qasm.count("rz(") == 3
