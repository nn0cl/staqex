"""Phase 1 Red test for LISS-0325: real NON_HERMITIAN_OPERATOR_ERROR check.

The existing positive regression (`i` used with no `parameter i: ...`
declaration still flags NON_HERMITIAN_OPERATOR_ERROR) is already covered by
`tests/test_h1_3_operator_ast_red.py::test_h1_3_non_hermitian_hamiltonian_is_rejected`
and is not duplicated here. This file covers only the new scenario: a
declared `parameter i: Real` must not be mistaken for the imaginary unit.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {str(diagnostic.get("code", "")) for diagnostic in compile_source(source).diagnostics}


def test_declared_real_parameter_named_i_is_not_flagged_non_hermitian() -> None:
    codes = _codes(
        """
        theory Valid {
          parameter i: Real
          operator H = i * Z
        }
        experiment run() { Measure H }
        """
    )

    assert "NON_HERMITIAN_OPERATOR_ERROR" not in codes
