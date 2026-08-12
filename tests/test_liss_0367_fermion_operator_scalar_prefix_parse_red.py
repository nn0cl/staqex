"""AT-TDD: LISS-0367 -- second-quantized RHS recognizes a parenthesized
atom behind a scalar prefix, not just a bare or unparenthesized-chain
form.

Design decision: docs/issues/LISS-0367-fermion-operator-scalar-prefix-parse.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402


def _wrap(decl: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        {decl}
        QubitOperator<Qubits> mapped = map(H, JordanWigner)
        State psi = |+>
        State psi = evolve {{ psi under mapped for 1.0.fs using Suzuki(order = 2, steps = 8) }}.run()
        measure psi
    }}
    """


def test_scalar_prefixed_parenthesized_atom_parses() -> None:
    src = _wrap(
        "FermionOperator<Orbitals> H = 1.0545718e-19 * (create[0] * annihilate[0])"
    )
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics


def test_scalar_prefixed_no_parens_still_parses() -> None:
    """Regression guard: LISS-0364's adopted workaround form."""
    src = _wrap(
        "FermionOperator<Orbitals> H = 1.0545718e-19 * create[0] * annihilate[0]"
    )
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics


def test_bare_atom_still_parses() -> None:
    """Regression guard: the pre-existing no-scalar-prefix form."""
    src = _wrap("FermionOperator<Orbitals> H = create[0] * annihilate[0]")
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics


def test_compound_coefficient_then_atom_still_parses() -> None:
    """Regression guard: the heuristic's originally-intended case --
    a genuine compound coefficient in parens, not the atom itself."""
    src = _wrap(
        """
        Float a = 1.0545718e-19
        Float b = 2.0
        FermionOperator<Orbitals> H = (a + b) * create[0] * annihilate[0]
        """
    )
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics
