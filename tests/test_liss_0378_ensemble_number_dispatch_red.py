"""AT-TDD: LISS-0378 -- Ensemble/RawMatrix numeric weights accept
folded literal BinOp and named Float/Int scalars (was spurious
MALFORMED_DENSITY_STATE).

Design decision: docs/issues/LISS-0378-ensemble-number-dispatch.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _codes(result) -> set[str]:
    return {diagnostic.get("code") for diagnostic in result.diagnostics}


def test_literal_ensemble_weight_remains_ok() -> None:
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


def test_binop_ensemble_weight_matches_literal() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            DensityState<Qubit> rho = DensityState(
                Ensemble([(1.0 * 1.0, |0>)])
            )
            POVM<Qubit> z = ComputationalBasis()
            Measure rho with z
        }
        """
    )
    assert "MALFORMED_DENSITY_STATE" not in _codes(result), result.diagnostics
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == {0: 1.0}


def test_named_float_ensemble_weight_matches_literal() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            Float w = 1.0
            DensityState<Qubit> rho = DensityState(Ensemble([(w, |0>)]))
            POVM<Qubit> z = ComputationalBasis()
            Measure rho with z
        }
        """
    )
    assert "MALFORMED_DENSITY_STATE" not in _codes(result), result.diagnostics
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == {0: 1.0}
