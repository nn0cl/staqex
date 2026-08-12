"""AT-TDD Phase 1 Red: LISS-0074 Slice D — hard unsupported qudit runtime."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source

KET = ">"

UNSUPPORTED = "UNSUPPORTED_LOCAL_DIMENSION"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def test_state_qutrit_measure_is_supported_d3_sv() -> None:
    """LISS-0112 Slice A lifts measure reject for State<Qutrit> (dim-3 SV)."""
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qutrit> s = |0{KET}
            measure s
        }}
        """
    )

    assert UNSUPPORTED not in _codes(compiled), compiled.diagnostics
    assert compiled.ok, compiled.diagnostics


def test_state_qudit3_measure_is_supported_d3_sv() -> None:
    """LISS-0112 Slice A lifts measure reject for State<Qudit<3>>."""
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qudit<3>> s = |1{KET}
            measure s
        }}
        """
    )

    assert UNSUPPORTED not in _codes(compiled), compiled.diagnostics
    assert compiled.ok, compiled.diagnostics


def test_qutrit_register_evolve_is_unsupported_local_dimension() -> None:
    """Operator<QutritRegister> must not lower to 2**n evolve."""
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            Operator<QutritRegister<1>> H = I
            State<Qutrit> s = |0{KET}
            State out = evolve {{ s under H for 0.1 using Suzuki(order = 2, steps = 1) }}.run()
            measure out
        }}
        """
    )

    assert UNSUPPORTED in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_apply_on_qutrit_is_unsupported_local_dimension() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qutrit> s = |0{KET}
            State out = apply(H, s)
            measure out
        }}
        """
    )

    assert UNSUPPORTED in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_qubit_state_measure_unchanged() -> None:
    """Slice D must not invent unsupported diagnostics for qubit carriers."""
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qubit> s = |0{KET}
            measure s
        }}
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert UNSUPPORTED not in _codes(compiled)


def main() -> None:
    test_state_qutrit_measure_is_supported_d3_sv()
    print("PASS test_state_qutrit_measure_is_supported_d3_sv")
    test_state_qudit3_measure_is_supported_d3_sv()
    print("PASS test_state_qudit3_measure_is_supported_d3_sv")
    test_qutrit_register_evolve_is_unsupported_local_dimension()
    print("PASS test_qutrit_register_evolve_is_unsupported_local_dimension")
    test_apply_on_qutrit_is_unsupported_local_dimension()
    print("PASS test_apply_on_qutrit_is_unsupported_local_dimension")
    test_qubit_state_measure_unchanged()
    print("PASS test_qubit_state_measure_unchanged")
    print("OK - LISS-0074 Slice D Phase 1 Red")


if __name__ == "__main__":
    main()
