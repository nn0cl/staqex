"""AT-TDD Phase 1 Red tests for symbolic Lindblad lowering."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def test_source_lindblad_lowers_operator_and_time_to_numeric_evolution() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            DensityState<Qubit> evolved = lindblad(rho, H, [], 0.1)
            Measure evolved
        }
        """
    )

    assert result.status == "succeeded", result.diagnostics
    envelope = result.measurements[0]
    assert envelope.marginal[1] > 0.009
    assert envelope.marginal[1] < 0.011


if __name__ == "__main__":
    test_source_lindblad_lowers_operator_and_time_to_numeric_evolution()
    print("OK — symbolic Lindblad Red tests")
