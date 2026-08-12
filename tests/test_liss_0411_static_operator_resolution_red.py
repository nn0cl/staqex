"""AT-TDD Phase 1 Red: static-analysis completion for the ADR 0206
Operator resolution gap -- unitarity_check.py's silent safety-gate
bypass and the QASM/Trotter backend's identical vague-error gap.

Target: docs/issues/LISS-0411-static-operator-resolution.md.

Both unitarity_check.py and backend/qasm/lower.py are pure static-AST
passes with no live Evaluator state -- they need their own,
compile-time-only struct-of-literals constant folding, separate from
(but sharing a helper with) LISS-0410's runtime fix.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.unitarity_check import check_unitarity  # noqa: E402


_NON_UNITARY_STRUCT_SOURCE = """
package t
struct W { a: Float }
pub fn main() -> Unit {
    W weights = W(2.0)
    Operator Bad = weights.a * X
    state psi = |0>
    state psi = apply(Bad, psi)
    measure psi
}
"""

_NON_UNITARY_LITERAL_SOURCE = """
package t
pub fn main() -> Unit {
    Operator Bad = 2.0 * X
    state psi = |0>
    state psi = apply(Bad, psi)
    measure psi
}
"""


def test_static_check_catches_non_unitary_struct_field_operator() -> None:
    """The exact case the code review found: `check` must not silently
    pass a struct-field-coefficient Operator that is genuinely
    non-unitary -- today it reports no diagnostics at all, unlike the
    physically identical bare-literal form."""
    compiled = compile_source(_NON_UNITARY_STRUCT_SOURCE)
    assert compiled.unit is not None, compiled.diagnostics
    diags = check_unitarity(compiled.unit)
    codes = {d["code"] for d in diags}
    assert "NON_UNITARY_TRANSFORM_ERROR" in codes, diags


def test_static_check_still_catches_the_literal_form() -> None:
    """Regression guard: the already-working bare-literal case must
    keep working exactly as before."""
    compiled = compile_source(_NON_UNITARY_LITERAL_SOURCE)
    assert compiled.unit is not None, compiled.diagnostics
    diags = check_unitarity(compiled.unit)
    codes = {d["code"] for d in diags}
    assert "NON_UNITARY_TRANSFORM_ERROR" in codes, diags


def test_static_check_does_not_false_positive_a_unitary_struct_field_operator() -> None:
    """A struct-field-coefficient Operator that genuinely is unitary
    must not be flagged."""
    source = """
    package t
    struct W { a: Float }
    pub fn main() -> Unit {
        W weights = W(1.0)
        Operator Good = weights.a * X
        state psi = |0>
        state psi = apply(Good, psi)
        measure psi
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    diags = check_unitarity(compiled.unit)
    codes = {d["code"] for d in diags}
    assert "NON_UNITARY_TRANSFORM_ERROR" not in codes, diags


def test_qasm_emission_resolves_the_liss_0407_nested_call_case() -> None:
    """ADR 0206's own regression case (`scale * f(weights)`) already
    runs fine via `evolve`; QASM emission must not still raise the
    pre-ADR-0206 vague `cannot compile sparse Pauli for OpCall`."""
    from compiler.staqex.pipeline import compile_source as _compile
    from compiler.staqex.backend.qasm.lower import lower_unit_to_circuit

    source = """
    package t
    struct W { a: Float }
    fn f(w: W) -> Operator {
        return w.a * Z[0]
    }
    pub fn main() -> Unit {
        W weights = W(0.5)
        Energy scale = 1.0.eV to J
        Operator H = scale * f(weights)
        state q = |0>
        Time dur = 0.6.fs
        state q = evolve q under H for dur
        measure q
    }
    """
    compiled = _compile(source)
    assert compiled.unit is not None, compiled.diagnostics
    circuit = lower_unit_to_circuit(compiled.unit)
    notes = " ".join(circuit.notes)
    assert "cannot compile sparse Pauli for OpCall" not in notes, notes
