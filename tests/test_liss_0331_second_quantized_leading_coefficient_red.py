"""AT-TDD: LISS-0331 -- FermionOperator RHS with a leading scalar
coefficient fails to parse.

`_type_first_bind`'s FermionOperator/BosonOperator/SpinOperator/
QubitOperator grammar dispatch only checked whether the very first token
was IDENT[ -- a leading coefficient (literal or named Float) routed the
whole expression through the wrong grammar.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _main(body: str) -> str:
    return f"""
package t
pub fn main() -> Unit {{
{body}
}}
"""


def _parse_errors(source: str) -> list[dict]:
    compiled = compile_source(source)
    return [d for d in compiled.diagnostics if d.get("code") == "PARSE_ERROR"]


def test_leading_numeric_literal_coefficient_parses() -> None:
    src = _main(
        """
    FermionOperator<Orbitals> H_fermion = 1.0 * create[0] * annihilate[0]
    QubitOperator<Qubits> H = map(H_fermion, JordanWigner)
    state a = |0>
    state a = evolve { a under H for 0.5 }.run()
    measure a
"""
    )

    assert _parse_errors(src) == []


def test_leading_named_float_coefficient_parses() -> None:
    src = _main(
        """
    Float e0 = 1.0
    FermionOperator<Orbitals> H_fermion = e0 * create[0] * annihilate[0]
    QubitOperator<Qubits> H = map(H_fermion, JordanWigner)
    state a = |0>
    state a = evolve { a under H for 0.5 }.run()
    measure a
"""
    )

    assert _parse_errors(src) == []


def test_leading_parenthesized_coefficient_expression_parses() -> None:
    src = _main(
        """
    Float e0 = 1.0
    Float e1 = 2.0
    FermionOperator<Orbitals> H_fermion = (e0 + e1) * create[0] * annihilate[0]
    QubitOperator<Qubits> H = map(H_fermion, JordanWigner)
    state a = |0>
    state a = evolve { a under H for 0.5 }.run()
    measure a
"""
    )

    assert _parse_errors(src) == []


def test_trailing_coefficient_form_is_unaffected() -> None:
    src = _main(
        """
    FermionOperator<Orbitals> H_fermion = create[0] * annihilate[0] * 1.0
    QubitOperator<Qubits> H = map(H_fermion, JordanWigner)
    state a = |0>
    state a = evolve { a under H for 0.5 }.run()
    measure a
"""
    )

    assert _parse_errors(src) == []


def test_map_binding_form_is_unaffected() -> None:
    src = _main(
        """
    FermionOperator<Orbitals> H_fermion = create[0] * annihilate[1]
    QubitOperator<Qubits> H = map(H_fermion, JordanWigner)
    state a = |0>
    state b = |0>
    state (a, b) = evolve { (a, b) under H for 0.5 }.run()
    measure a tracing_out b
"""
    )

    assert _parse_errors(src) == []
