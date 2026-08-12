"""AT-TDD Phase 1 Red: LISS-0014 interface impl and system boundary."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_explicit_impl_and_inline_generic_bound_are_accepted() -> None:
    compiled = compile_source(
        """
        package t
        interface System {}
        interface Evolvable<T> {
            fn advance(x: State<T>) -> State<T>
        }
        class Oscillator : System {}
        impl Evolvable<Float> for Oscillator {
            fn advance(x: State<Float>) -> State<Float> {
                return x
            }
        }
        fn lift<T: System>(x: State<T>) -> State<T> {
            return x
        }
        pub fn main() -> Unit {
            State psi = dirac(0.0)
            measure psi
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_system_is_a_marker_without_required_methods() -> None:
    compiled = compile_source(
        """
        package t
        interface System {}
        class EmptySystem : System {}
        pub fn main() -> Unit {
            State result = dirac(0)
            measure result
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_duplicate_interface_type_impls_are_rejected_after_merge() -> None:
    codes = _codes(
        """
        package t
        interface System {}
        class Oscillator : System {}
        impl System for Oscillator {}
        impl System for Oscillator {}
        pub fn main() -> Unit {
            State result = dirac(0)
            measure result
        }
        """
    )

    assert "IMPL_COHERENCE_ERROR" in codes


def test_impl_methods_cannot_declare_pub() -> None:
    codes = _codes(
        """
        package t
        interface Evolvable<T> {
            fn advance(x: State<T>) -> State<T>
        }
        class Oscillator {}
        impl Evolvable<Float> for Oscillator {
            pub fn advance(x: State<Float>) -> State<Float> {
                return x
            }
        }
        pub fn main() -> Unit {
            State result = dirac(0.0)
            measure result
        }
        """
    )

    assert "IMPL_VISIBILITY_ERROR" in codes


def test_system_is_not_a_general_value_constructor() -> None:
    codes = _codes(
        """
        package t
        interface System {}
        pub fn main() -> Unit {
            System value = System()
            State result = dirac(0)
            measure result
        }
        """
    )

    assert "SYSTEM_EXPRESSION_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_explicit_impl_and_inline_generic_bound_are_accepted,
        test_system_is_a_marker_without_required_methods,
        test_duplicate_interface_type_impls_are_rejected_after_merge,
        test_impl_methods_cannot_declare_pub,
        test_system_is_not_a_general_value_constructor,
    ):
        test()
    print("OK — trait impl/system Red tests")
