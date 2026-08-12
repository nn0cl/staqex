"""AT-TDD: LISS-0372 -- `apply(rx(theta), q)` resolves a named classical
scalar angle, not just a literal (was silently dropping the gate from
the emitted QASM, with both compiled.ok and emitted.ok reporting True).

Design decision: docs/issues/LISS-0372-rx-angle-silent-gate-drop.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402
from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402


def _src(angle_expr: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        QubitRegister<1> register = system()
        {'' if angle_expr != 'theta' else 'Float theta = 1.57'}
        State q = |0>
        State q = apply(rx({angle_expr}), q)
        Measure q
    }}
    """


def test_named_variable_angle_emits_the_same_gate_as_the_literal() -> None:
    literal_src = _src("1.57")
    named_src = _src("theta")

    literal_compiled = compile_source(literal_src)
    assert literal_compiled.ok, literal_compiled.diagnostics
    literal_emitted = QASM3Emitter(route=False).emit_unit(literal_compiled.unit)
    assert literal_emitted.ok, literal_emitted.notes
    assert "rx(1.57)" in literal_emitted.qasm, literal_emitted.qasm

    named_compiled = compile_source(named_src)
    assert named_compiled.ok, named_compiled.diagnostics
    named_emitted = QASM3Emitter(route=False).emit_unit(named_compiled.unit)
    assert named_emitted.ok, named_emitted.notes
    assert "rx(1.57)" in named_emitted.qasm, named_emitted.qasm


def test_unresolvable_angle_is_explicitly_rejected_not_silently_dropped() -> None:
    """Regression guard: an unresolvable angle must not silently vanish
    from the circuit -- it must be explicitly rejected instead."""
    source = _src("unbound_name")
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert not emitted.ok, "an unresolvable rotation angle must not silently emit ok=True"
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "QASM_ROTATION_ANGLE_UNRESOLVED", emitted.circuit.reject_code
    assert "rx(" not in emitted.qasm
