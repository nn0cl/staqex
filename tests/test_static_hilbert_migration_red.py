"""AT-TDD Phase 1 Red: LISS-0029 static Hilbert migration/resource boundary.

These tests lock the remaining acceptance boundary without adding production
behavior.  The historical ``register(N)`` fixture must not become the
normative spelling, and resource overflow must be diagnosed rather than
silently truncated.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_historical_register_call_is_not_a_compatibility_alias() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            ForEach q in register(3) {
                apply(H, q)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "STATIC_HILBERT_SURFACE_ERROR" in codes


def test_static_register_resource_overflow_is_a_hard_diagnostic() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1000000> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "STATIC_HILBERT_RESOURCE_ERROR" in codes


def test_static_hilbert_overflow_never_silently_truncates() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<1000000> reg = system()
        ForEach q in reg {
            apply(H, q)
        }
        State<Int> observed = Coin()
        Measure observed
    }
    """

    compiled = compile_source(source)

    assert not compiled.ok
    assert "STATIC_HILBERT_RESOURCE_ERROR" in _codes(source)


if __name__ == "__main__":
    for test in (
        test_historical_register_call_is_not_a_compatibility_alias,
        test_static_register_resource_overflow_is_a_hard_diagnostic,
        test_static_hilbert_overflow_never_silently_truncates,
    ):
        test()
    print("OK — static Hilbert migration/resource Red tests")
