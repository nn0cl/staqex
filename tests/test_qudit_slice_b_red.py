"""AT-TDD Phase 1 Red: LISS-0074 Slice B — ket/bra label vs local dimension."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source

KET = ">"
BRA = "<"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def test_in_range_labels_on_qutrit_accepted() -> None:
    for label in ("0", "1", "2"):
        compiled = compile_source(
            f"""
            package t
            pub fn main() -> Unit {{
                State<Qutrit> s = |{label}{KET}
                State s = |0>
                State observed = Coin()
                Measure observed
            }}
            """
        )
        assert compiled.ok, (label, compiled.diagnostics)
        assert "LOCAL_DIMENSION_TYPE_ERROR" not in _codes(compiled)


def test_out_of_range_ket_on_qutrit_is_local_dimension_type_error() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qutrit> s = |3{KET}
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert "LOCAL_DIMENSION_TYPE_ERROR" in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_out_of_range_ket_on_qudit4_is_error() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qudit<4>> s = |4{KET}
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert "LOCAL_DIMENSION_TYPE_ERROR" in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_in_range_ket_on_qudit4_accepted() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qudit<4>> s = |3{KET}
            State s = |0>
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_out_of_range_bra_on_qutrit_is_error() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qutrit> b = {BRA}3|
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert "LOCAL_DIMENSION_TYPE_ERROR" in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_alone_ket_without_qudit_carrier_unchanged() -> None:
    """Slice B must not invent a global dim-2 check for untyped alone kets."""
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State s = |1{KET}
            State s = |0>
            State observed = Coin()
            Measure observed
        }}
        """
    )

    assert compiled.ok, compiled.diagnostics


def main() -> None:
    test_in_range_labels_on_qutrit_accepted()
    print("PASS test_in_range_labels_on_qutrit_accepted")
    test_out_of_range_ket_on_qutrit_is_local_dimension_type_error()
    print("PASS test_out_of_range_ket_on_qutrit_is_local_dimension_type_error")
    test_out_of_range_ket_on_qudit4_is_error()
    print("PASS test_out_of_range_ket_on_qudit4_is_error")
    test_in_range_ket_on_qudit4_accepted()
    print("PASS test_in_range_ket_on_qudit4_accepted")
    test_out_of_range_bra_on_qutrit_is_error()
    print("PASS test_out_of_range_bra_on_qutrit_is_error")
    test_alone_ket_without_qudit_carrier_unchanged()
    print("PASS test_alone_ket_without_qudit_carrier_unchanged")
    print("OK - LISS-0074 Slice B Phase 1 Red")


if __name__ == "__main__":
    main()
