"""AT-TDD: LISS-0368 -- Jordan-Wigner mapping accepts named orbital
indices and compound coefficient sums.

Design decision: docs/issues/LISS-0368-jw-mapping-scalar-index-robustness.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import run_source  # noqa: E402

_K = "1.0545718e-19"


def _wrap(decl: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        {decl}
        QubitOperator<Qubits> mapped = map(H, JordanWigner)
        state psi = |+>
        state psi = evolve {{ psi under mapped for 1.0.fs using Suzuki(order = 2, steps = 8) }}.run()
        measure psi
    }}
    """


def test_named_integer_orbital_index_is_accepted() -> None:
    src = _wrap(
        f"""
        Int site = 0
        FermionOperator<Orbitals> H = {_K} * create[site] * annihilate[site]
        """
    )
    result = run_source(src, settings={"seed": 7})
    assert result.status == "succeeded", result.diagnostics


def test_compound_sum_coefficient_is_accepted() -> None:
    src = _wrap(
        f"""
        Float a = {_K}
        Float b = 2.0e-20
        FermionOperator<Orbitals> H = (a + b) * create[0] * annihilate[0]
        """
    )
    result = run_source(src, settings={"seed": 7})
    assert result.status == "succeeded", result.diagnostics


def test_literal_orbital_index_still_works() -> None:
    """Regression guard: the pre-existing literal-index form."""
    src = _wrap(f"FermionOperator<Orbitals> H = {_K} * create[0] * annihilate[0]")
    result = run_source(src, settings={"seed": 7})
    assert result.status == "succeeded", result.diagnostics


def test_single_variable_coefficient_still_works() -> None:
    """Regression guard: the pre-existing single-named-scalar coefficient form."""
    src = _wrap(
        f"""
        Float e0 = {_K}
        FermionOperator<Orbitals> H = e0 * create[0] * annihilate[0]
        """
    )
    result = run_source(src, settings={"seed": 7})
    assert result.status == "succeeded", result.diagnostics
