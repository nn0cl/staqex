"""AT-TDD acceptance tests for the density/CPTP/Lindblad boundary."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_density_state_and_typed_cptp_channel_have_distinct_contracts() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Qubit> psi = |0>
            DensityState<Qubit> rho = pure_to_density(psi)
            Channel<Qubit, Qubit> noise = DepolarizingChannel(0.1)
            DensityState<Qubit> evolved = apply(noise, rho)
            Measure evolved
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.mixed_state_contracts is not None
    assert compiled.mixed_state_contracts["rho"].kind == "DensityState"
    assert compiled.mixed_state_contracts["noise"].kind == "Channel"


def test_partial_trace_and_lindblad_require_mixed_state_lane() -> None:
    reduced = compile_source(
        """
        package t
        pub fn main() -> Unit {
            DensityState<Qubit> rho = mixed(|0>, |1>)
            DensityState<Qubit> reduced = partial_trace(rho, subsystem)
            Measure reduced
        }
        """
    )
    evolved = compile_source(
        """
        package t
        pub fn main() -> Unit {
            DensityState<Qubit> rho = mixed(|0>, |1>)
            DensityState<Qubit> evolved = lindblad(rho, H, jumps, t)
            Measure evolved
        }
        """
    )

    assert reduced.ok, reduced.diagnostics
    assert evolved.ok, evolved.diagnostics
    assert reduced.mixed_state_contracts["reduced"].operation == "partial_trace"
    assert evolved.mixed_state_contracts["evolved"].operation == "lindblad"


def test_pure_state_surface_does_not_gain_implicit_noise() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State<Qubit> psi = |0>
            DensityState<Qubit> rho = apply(DepolarizingChannel(0.1), psi)
            Measure rho
        }
        """
    )

    assert "MIXED_STATE_TYPE_ERROR" in codes


if __name__ == "__main__":
    test_density_state_and_typed_cptp_channel_have_distinct_contracts()
    test_partial_trace_and_lindblad_require_mixed_state_lane()
    test_pure_state_surface_does_not_gain_implicit_noise()
    print("OK — density/CPTP/Lindblad Red tests")
