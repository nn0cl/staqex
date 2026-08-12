"""AT-TDD Phase 1 Red tests for symbolic Lindblad jump lowering."""

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


def test_source_lowers_bound_operator_jump() -> None:
    result = run_source(
        _main(
            """
            Operator H = X
            Operator decay = X
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[0.0, 0.0], [0.0, 1.0]])
            )
            DensityState<Qubit> evolved = lindblad(
                rho, H, JumpSet([decay]), 0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal.get(0, 0.0) > 0.0


def test_source_applies_multiple_symbolic_jumps() -> None:
    result = run_source(
        _main(
            """
            Operator H = X
            Operator first = X
            Operator second = Z
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[0.0, 0.0], [0.0, 1.0]])
            )
            DensityState<Qubit> evolved = lindblad(
                rho, H, JumpSet([first, second]), 0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "succeeded", result.diagnostics
    assert result.metadata["execution_lane"] == "cpu/simulator"


def test_source_rejects_unresolved_symbolic_jump() -> None:
    result = run_source(
        _main(
            """
            Operator H = X
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            DensityState<Qubit> evolved = lindblad(
                rho, H, JumpSet([missing_jump]), 0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "failed"
    assert "SYMBOLIC_JUMP_LOWERING_REQUIRED" in _codes(result)


def test_source_rejects_symbolic_jump_dimension_mismatch() -> None:
    result = run_source(
        _main(
            """
            Operator H = X
            Operator invalid = (X[1])
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            DensityState<Qubit> evolved = lindblad(
                rho, H, JumpSet([invalid]), 0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "failed"
    assert "LINDBLAD_JUMP_DIMENSION_ERROR" in _codes(result)


def test_source_rejects_channel_as_symbolic_jump() -> None:
    result = run_source(
        _main(
            """
            Operator H = X
            Channel<Qubit, Qubit> channel = KrausChannel([
                [[1.0, 0.0], [0.0, 1.0]]
            ])
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            DensityState<Qubit> evolved = lindblad(
                rho, H, JumpSet([channel]), 0.1
            )
            Measure evolved
            """
        )
    )

    assert result.status == "failed"
    codes = _codes(result)
    assert "INVALID_LINDBLAD_JUMP_SET" in codes
    assert "INCOMPLETE_KRAUS_CHANNEL" not in codes


if __name__ == "__main__":
    for test in (
        test_source_lowers_bound_operator_jump,
        test_source_applies_multiple_symbolic_jumps,
        test_source_rejects_unresolved_symbolic_jump,
        test_source_rejects_symbolic_jump_dimension_mismatch,
        test_source_rejects_channel_as_symbolic_jump,
    ):
        test()
    print("OK — symbolic Lindblad jump lowering Red tests")
