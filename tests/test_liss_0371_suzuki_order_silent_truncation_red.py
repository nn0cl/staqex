"""AT-TDD: LISS-0371 -- `using Suzuki(order = ...)` resolves a named
classical constant, not just a bare literal (was spuriously rejected
with SUZUKI_ORDER_ERROR for a named-variable order equal to a literal
one -- corrected from an earlier, incorrect "silent downgrade" framing;
see the Design decision section for the re-verification).

Design decision: docs/issues/LISS-0371-suzuki-order-silent-truncation.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402
from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402


def _src(order_expr: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        QubitRegister<1> register = system()
        {'' if order_expr != 'ord' else 'Int ord = 4'}
        Operator H = Z[0]
        State a = |+>
        State a = Evolve {{ a under H for 0.1 using Suzuki(order = {order_expr}, steps = 3) }}.run()
        Measure a
    }}
    """


def _rz_count(source: str) -> int:
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert emitted.ok, emitted.notes
    return emitted.qasm.count("rz(")


def test_named_variable_order_emits_the_same_gate_count_as_the_literal() -> None:
    literal_count = _rz_count(_src("4"))
    named_count = _rz_count(_src("ord"))
    assert literal_count == 15, literal_count  # S4 formula, 5 rz per sub-step x 3
    assert named_count == literal_count, (named_count, literal_count)


def test_qpu_ir_lowering_policy_reports_the_correct_order() -> None:
    source = _src("ord")
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    policy = compiled.qpu_ir.get("lowering_policy")
    assert policy is not None, compiled.diagnostics
    assert policy["order"] == 4, policy


def test_unresolvable_order_still_falls_back_to_2() -> None:
    """Regression guard: the fallback *behavior* for a genuinely
    unresolvable order expression is unchanged -- only recognition of
    resolvable expressions is widened."""
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<1> register = system()
        Operator H = Z[0]
        State a = |+>
        State a = Evolve { a under H for 0.1 using Suzuki(order = unbound_name, steps = 3) }.run()
        Measure a
    }
    """
    compiled = compile_source(source)
    codes = {d.get("code") for d in compiled.diagnostics}
    if compiled.ok:
        emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
        assert emitted.ok, emitted.notes
        assert emitted.qasm.count("rz(") == 3, emitted.qasm  # S2 fallback
    else:
        assert codes, compiled.diagnostics
