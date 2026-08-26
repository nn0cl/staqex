"""AT-TDD Phase 1 Red: LISS-0013 pipeline and currying boundary."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_pipeline_is_left_associative_and_preserves_state() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = Dirac(0)
            State psi = |0>
            State result = psi |> phase(0.5) |> phase(0.25)
            Measure result
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_pipeline_rejects_measurement_or_rng_effects() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = Dirac(0)
            State result = psi |> Measure
            Measure result
        }
        """
    )

    assert "PIPE_EFFECT_ERROR" in codes


def test_pipeline_does_not_implicitly_convert_an_operator_to_a_function() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State psi = Dirac(0)
            Operator H = X
            State result = psi |> H
            Measure result
        }
        """
    )

    assert "PIPE_CALLABLE_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_pipeline_is_left_associative_and_preserves_state,
        test_pipeline_rejects_measurement_or_rng_effects,
        test_pipeline_does_not_implicitly_convert_an_operator_to_a_function,
    ):
        test()
    print("OK — pipeline/currying Red tests")
