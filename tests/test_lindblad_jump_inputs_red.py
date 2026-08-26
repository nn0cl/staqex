"""AT-TDD Phase 1 Red tests for explicit Lindblad jump inputs."""

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


def _codes(result) -> set[str]:
    return {diagnostic.get("code") for diagnostic in result.diagnostics}


def test_source_accepts_non_empty_numeric_jump_set() -> None:
    result = run_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[0.0, 0.0], [0.0, 1.0]])
            )
            Operator H = X
            DensityState<Qubit> evolved = lindblad(
                rho, H,
                JumpSet([RawMatrix([[0.0, 1.0], [0.0, 0.0]])]),
                0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "succeeded", result.diagnostics
    # The decay jump must transfer population from |1> to |0>.
    assert result.measurements[0].marginal.get(0, 0.0) > 0.0


def test_source_rejects_jump_with_wrong_hilbert_dimension() -> None:
    result = run_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            DensityState<Qubit> evolved = lindblad(
                rho, X,
                JumpSet([RawMatrix([
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0],
                    [0.0, 0.0, 0.0]
                ])]),
                0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "failed"
    assert "LINDBLAD_JUMP_DIMENSION_ERROR" in _codes(result)


def test_source_rejects_malformed_jump_payload_without_repair() -> None:
    result = run_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            DensityState<Qubit> evolved = lindblad(
                rho, X,
                JumpSet([RawMatrix([[0.0, 1.0], [0.0]])]),
                0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "failed"
    assert "INVALID_LINDBLAD_JUMP_SET" in _codes(result)


def test_unresolved_symbolic_jump_remains_opaque() -> None:
    result = run_source(
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

    assert result.status == "succeeded", result.diagnostics
    assert result.metadata["execution_lane"] == "cpu/simulator"
    assert "density_matrix" not in result.metadata


def test_channel_completeness_diagnostic_is_not_reused_for_jumps() -> None:
    result = run_source(
        _main(
            """
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            DensityState<Qubit> evolved = lindblad(
                rho, X,
                JumpSet([KrausChannel([
                    RawMatrix([[1.0, 0.0], [0.0, 0.0]])
                ])]),
                0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "failed"
    codes = _codes(result)
    assert "INCOMPLETE_KRAUS_CHANNEL" not in codes
    assert "INVALID_LINDBLAD_JUMP_SET" in codes


if __name__ == "__main__":
    for test in (
        test_source_accepts_non_empty_numeric_jump_set,
        test_source_rejects_jump_with_wrong_hilbert_dimension,
        test_source_rejects_malformed_jump_payload_without_repair,
        test_unresolved_symbolic_jump_remains_opaque,
        test_channel_completeness_diagnostic_is_not_reused_for_jumps,
    ):
        test()
    print("OK — Lindblad jump input Red tests")
