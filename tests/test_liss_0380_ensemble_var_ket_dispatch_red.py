"""AT-TDD: LISS-0380 -- Ensemble Var ket states resolve like KetLit.

Design decision: docs/issues/LISS-0380-ensemble-var-ket-dispatch.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def test_ensemble_ketlit_remains_ok() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            DensityState<Qubit> rho = DensityState(Ensemble([(1.0, |0>)]))
            POVM<Qubit> z = ComputationalBasis()
            Measure rho with z
        }
        """
    )
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == {0: 1.0}


def test_ensemble_var_ket_matches_ketlit() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State<Qubit> psi = |0>
            DensityState<Qubit> rho = DensityState(Ensemble([(1.0, psi)]))
            POVM<Qubit> z = ComputationalBasis()
            Measure rho with z
        }
        """
    )
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == {0: 1.0}
