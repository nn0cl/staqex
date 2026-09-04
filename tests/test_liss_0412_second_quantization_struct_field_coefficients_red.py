"""AT-TDD Phase 1 Red: struct-field coefficients in second-quantized
(Jordan-Wigner) expressions.

Target: docs/issues/LISS-0412-second-quantization-struct-field-coefficients.md.

Independent-context code review (this session) found two separate bugs
blocking the same physics need -- a physicist attaching a struct-field
coefficient to a FermionOperator term:

1. Parser: `_second_quantized_rhs_is_op_dsl`'s bounded lookahead only
   recognizes a bare literal or identifier as a coefficient term, not a
   dotted struct-field chain (`weights.e0`) -- the unparenthesized
   natural form misroutes to the wrong grammar and fails with an
   unrelated PARSE_ERROR.
2. `second_quantization.py::_scalar_value` doesn't recognize `OpAttr` as
   a scalar coefficient at all (even with parens routing around bug 1),
   so Jordan-Wigner mapping fails with
   `SECOND_QUANTIZATION_MAPPING_UNSUPPORTED`.
"""

from __future__ import annotations

from canonical_execution import run_canonical

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelError  # noqa: E402


_UNPARENTHESIZED_SOURCE = """
package t
struct W { e0: Float }
pub fn main() -> Unit {
    W weights = W(1.0)
    FermionOperator<Orbitals> H_fermion = weights.e0 * create[0] * annihilate[0]
    QubitOperator<Qubits> H_raw = map(H_fermion, JordanWigner)
    Energy scale = 1.0.eV to J
    Operator H = scale * H_raw
    State a = |0>
    State a = Evolve { a under H for 0.5.fs }.run()
    Measure a
}
"""


def test_unparenthesized_struct_field_coefficient_parses() -> None:
    """The natural, unparenthesized form must parse -- today it
    misroutes to the wrong grammar and fails with an unrelated
    `function result expression must be the final item in a block`."""
    compiled = compile_source(_UNPARENTHESIZED_SOURCE)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "PARSE_ERROR" not in codes, compiled.diagnostics


def test_struct_field_coefficient_resolves_and_runs() -> None:
    """Once parsed, the struct-field coefficient must actually resolve
    through Jordan-Wigner mapping and run -- today (even with a
    parenthesized workaround bypassing the parser bug) this raises
    `SECOND_QUANTIZATION_MAPPING_UNSUPPORTED: \\`OpAttr\\` is not covered`."""
    compiled = compile_source(_UNPARENTHESIZED_SOURCE)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None


def test_struct_field_coefficient_matches_equivalent_literal_value() -> None:
    """Regression/correctness guard: a struct field holding 1.0 must
    produce the identical terminal distribution as the literal `1.0`
    already-working form -- the coefficient must actually reach the
    mapped Hamiltonian, not be silently dropped or defaulted."""
    literal_source = """
    package t
    pub fn main() -> Unit {
        FermionOperator<Orbitals> H_fermion = 1.0 * create[0] * annihilate[0]
        QubitOperator<Qubits> H_raw = map(H_fermion, JordanWigner)
        Energy scale = 1.0.eV to J
        Operator H = scale * H_raw
        State a = |0>
        State a = Evolve { a under H for 0.5.fs }.run()
        Measure a
    }
    """
    struct_compiled = compile_source(_UNPARENTHESIZED_SOURCE)
    literal_compiled = compile_source(literal_source)
    assert struct_compiled.unit is not None, struct_compiled.diagnostics
    assert literal_compiled.unit is not None, literal_compiled.diagnostics

    struct_result = run_canonical(struct_compiled, Evaluator(seed=0))
    literal_result = run_canonical(literal_compiled, Evaluator(seed=0))
    assert struct_result.measure is not None
    assert literal_result.measure is not None
    assert struct_result.measure.marginal == literal_result.measure.marginal


def test_existing_leading_coefficient_forms_still_parse() -> None:
    """Regression guard: LISS-0331/0367's own already-working forms
    (bare literal, named Float, parenthesized compound) must be
    unaffected by extending the lookahead for dotted struct fields."""
    literal_source = """
    package t
    pub fn main() -> Unit {
        FermionOperator<Orbitals> H_fermion = 1.0 * create[0] * annihilate[0]
        QubitOperator<Qubits> H_raw = map(H_fermion, JordanWigner)
        Energy scale = 1.0.eV to J
        Operator H = scale * H_raw
        State a = |0>
        State a = Evolve { a under H for 0.5.fs }.run()
        Measure a
    }
    """
    named_source = """
    package t
    pub fn main() -> Unit {
        Float e0 = 1.0
        FermionOperator<Orbitals> H_fermion = e0 * create[0] * annihilate[0]
        QubitOperator<Qubits> H_raw = map(H_fermion, JordanWigner)
        Energy scale = 1.0.eV to J
        Operator H = scale * H_raw
        State a = |0>
        State a = Evolve { a under H for 0.5.fs }.run()
        Measure a
    }
    """
    compound_source = """
    package t
    pub fn main() -> Unit {
        Float e0 = 0.5
        Float e1 = 0.5
        FermionOperator<Orbitals> H_fermion = (e0 + e1) * create[0] * annihilate[0]
        QubitOperator<Qubits> H_raw = map(H_fermion, JordanWigner)
        Energy scale = 1.0.eV to J
        Operator H = scale * H_raw
        State a = |0>
        State a = Evolve { a under H for 0.5.fs }.run()
        Measure a
    }
    """
    for src in (literal_source, named_source, compound_source):
        compiled = compile_source(src)
        codes = {d.get("code") for d in compiled.diagnostics}
        assert "PARSE_ERROR" not in codes, compiled.diagnostics
