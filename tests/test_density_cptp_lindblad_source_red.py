"""AT-TDD Phase 1 Red tests for source-level mixed-state execution."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _main(body: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        {body}
    }}
    """


def test_source_density_measure_returns_opaque_mixed_job_result() -> None:
    result = run_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                Ensemble([
                    (0.5, |0>),
                    (0.5, |1>)
                ])
            )
            Measure rho
            """
        )
    )

    assert result.status == "succeeded", result.diagnostics
    assert len(result.measurements) == 1
    assert result.metadata["state_type"] == "DensityState"
    assert "density_matrix" not in result.metadata


def test_source_lindblad_executes_on_cpu_lane_before_terminal_measure() -> None:
    result = run_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                Ensemble([(1.0, |1>)])
            )
            DensityState<Qubit> evolved = lindblad(rho, H, jumps, t)
            Measure evolved
            """
        ),
        settings={"target": "cpu"},
    )

    assert result.status == "succeeded", result.diagnostics
    assert result.metadata["execution_lane"] == "cpu/simulator"


def test_source_pure_state_channel_mixing_remains_hard_rejected() -> None:
    result = run_source(
        _main(
            """
            State<Qubit> psi = |0>
            DensityState<Qubit> rho = apply(DepolarizingChannel(0.1), psi)
            Measure rho
            """
        )
    )

    assert result.status == "failed"
    assert any(
        diagnostic.get("code") == "MIXED_STATE_TYPE_ERROR"
        for diagnostic in result.diagnostics
    )


if __name__ == "__main__":
    test_source_density_measure_returns_opaque_mixed_job_result()
    test_source_lindblad_executes_on_cpu_lane_before_terminal_measure()
    test_source_pure_state_channel_mixing_remains_hard_rejected()
    print("OK — source-level mixed-state Red tests")
