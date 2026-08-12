"""AT-TDD Phase 1 Red tests for the LISS-0011 numeric slice."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def _main(body: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        {body}
    }}
    """


def test_reject_non_trace_one_density_matrix() -> None:
    codes = _codes(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[0.8, 0.0], [0.0, 0.5]])
            )
            Measure rho
            """
        )
    )

    assert "MALFORMED_DENSITY_STATE" in codes


def test_reject_non_positive_density_matrix() -> None:
    codes = _codes(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.2, 0.0], [0.0, -0.2]])
            )
            Measure rho
            """
        )
    )

    assert "MALFORMED_DENSITY_STATE" in codes


def test_accept_valid_ensemble() -> None:
    compiled = compile_source(
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

    assert compiled.ok, compiled.diagnostics


def test_accept_valid_raw_matrix() -> None:
    compiled = compile_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[0.5, 0.0], [0.0, 0.5]])
            )
            Measure rho
            """
        )
    )

    assert compiled.ok, compiled.diagnostics


def test_reject_incomplete_kraus_channel_before_application() -> None:
    codes = _codes(
        _main(
            """
            Channel<Qubit, Qubit> channel = KrausChannel([K0])
            DensityState<Qubit> rho = DensityState(
                Ensemble([(1.0, |0>)])
            )
            DensityState<Qubit> evolved = apply(channel, rho)
            Measure evolved
            """
        )
    )

    assert "INCOMPLETE_KRAUS_CHANNEL" in codes


def test_lindblad_numeric_lane_is_explicitly_constructible() -> None:
    compiled = compile_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                Ensemble([(1.0, |0>)])
            )
            DensityState<Qubit> evolved = lindblad(rho, H, jumps, t)
            Measure evolved
            """
        )
    )

    assert compiled.ok, compiled.diagnostics


if __name__ == "__main__":
    for test in (
        test_reject_non_trace_one_density_matrix,
        test_reject_non_positive_density_matrix,
        test_accept_valid_ensemble,
        test_accept_valid_raw_matrix,
        test_reject_incomplete_kraus_channel_before_application,
        test_lindblad_numeric_lane_is_explicitly_constructible,
    ):
        test()
    print("OK — density/CPTP/Lindblad numeric Red tests")
