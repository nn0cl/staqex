"""AT-TDD Phase 1 Red: LISS-0015 effect marking and propagation."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_effect_annotation_is_accepted_on_a_function() -> None:
    compiled = compile_source(
        """
        package t
        fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
            return inspect(x)
        }
        pub fn main() -> Unit {
            State psi = dirac(0.0)
            State viewed = inspect_state(psi)
            measure viewed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_pure_function_cannot_call_an_inspect_effect() -> None:
    codes = _codes(
        """
        package t
        fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
            return inspect(x)
        }
        fn pure_wrapper(x: State<Float>) -> State<Float> {
            return inspect_state(x)
        }
        pub fn main() -> Unit {
            State psi = dirac(0.0)
            State viewed = pure_wrapper(psi)
            measure viewed
        }
        """
    )

    assert "EFFECT_VIOLATION_ERROR" in codes


def test_measure_effect_cannot_return_a_state_value() -> None:
    codes = _codes(
        """
        package t
        fn observe_state(x: State<Float>) -> State<Float> effects { Measure } {
            measure x
            return x
        }
        pub fn main() -> Unit {
            State psi = dirac(0.0)
            State observed = observe_state(psi)
            measure observed
        }
        """
    )

    assert "EFFECT_MEASURE_RETURN_ERROR" in codes


def test_effects_propagate_through_a_pipeline_stage() -> None:
    codes = _codes(
        """
        package t
        fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
            return inspect(x)
        }
        pub fn main() -> Unit {
            State psi = dirac(0.0)
            State viewed = psi |> inspect_state()
            measure viewed
        }
        """
    )

    assert "PIPE_EFFECT_ERROR" in codes or "EFFECT_VIOLATION_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_effect_annotation_is_accepted_on_a_function,
        test_pure_function_cannot_call_an_inspect_effect,
        test_measure_effect_cannot_return_a_state_value,
        test_effects_propagate_through_a_pipeline_stage,
    ):
        test()
    print("OK — effect marking Red tests")
