"""AT-TDD Phase 1 Red: LISS-0074 Slice A — qutrit/qudit type surface."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source

EBNF_PATH = _REPO / "docs" / "specs" / "grammar" / "staqex.ebnf"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def test_valid_qutrit_and_qudit_state_types_accepted() -> None:
    for annotation in ("Qutrit", "Qudit<3>"):
        compiled = compile_source(
            f"""
            package t
            pub fn main() -> Unit {{
                State<{annotation}> s = |0>
                State s = |0>
                State observed = coin()
                measure observed
            }}
            """
        )
        assert compiled.ok, (annotation, compiled.diagnostics)
        assert "LOCAL_DIMENSION_TYPE_ERROR" not in _codes(compiled)
        assert "STATIC_REGISTER_TYPE_ERROR" not in _codes(compiled)


def test_valid_qutrit_and_qudit_registers_accepted() -> None:
    sources = [
        "QutritRegister<1> r = system()",
        "QuditRegister<3, 1> r = system()",
        "QuditRegister<4, 2> r = system()",
    ]
    for bind in sources:
        compiled = compile_source(
            f"""
            package t
            pub fn main() -> Unit {{
                {bind}
                State observed = coin()
                measure observed
            }}
            """
        )
        assert compiled.ok, (bind, compiled.diagnostics)
        assert "LOCAL_DIMENSION_TYPE_ERROR" not in _codes(compiled)


def test_qudit_zero_dimension_is_local_dimension_type_error() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Qudit<0>> s = |0>
            State observed = coin()
            measure observed
        }
        """
    )

    assert "LOCAL_DIMENSION_TYPE_ERROR" in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_qudit_register_nonpositive_shape_is_error() -> None:
    cases = [
        "QuditRegister<0, 1> r = system()",
        "QuditRegister<3, 0> r = system()",
        "QutritRegister<0> r = system()",
    ]
    for bind in cases:
        compiled = compile_source(
            f"""
            package t
            pub fn main() -> Unit {{
                {bind}
                State observed = coin()
                measure observed
            }}
            """
        )
        codes = _codes(compiled)
        assert (
            "LOCAL_DIMENSION_TYPE_ERROR" in codes
            or "STATIC_REGISTER_TYPE_ERROR" in codes
        ), (bind, compiled.diagnostics)
        assert not compiled.ok


def test_qudit_arity_mismatch_is_local_dimension_type_error() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Qudit> s = |0>
            State observed = coin()
            measure observed
        }
        """
    )

    assert "LOCAL_DIMENSION_TYPE_ERROR" in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_qudit_register_arity_mismatch_is_error() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QuditRegister<3> r = system()
            State observed = coin()
            measure observed
        }
        """
    )

    codes = _codes(compiled)
    assert (
        "LOCAL_DIMENSION_TYPE_ERROR" in codes or "STATIC_REGISTER_TYPE_ERROR" in codes
    ), compiled.diagnostics
    assert not compiled.ok


def test_ebnf_documents_qutrit_qudit_types() -> None:
    text = EBNF_PATH.read_text(encoding="utf-8")
    assert "Qutrit" in text or "qutrit" in text.lower()
    assert "Qudit" in text or "qudit" in text.lower()
    assert re.search(
        r"QutritRegister|QuditRegister|local.?dim",
        text,
        re.IGNORECASE,
    ), "EBNF must document qutrit/qudit register shapes"


def main() -> None:
    test_valid_qutrit_and_qudit_state_types_accepted()
    print("PASS test_valid_qutrit_and_qudit_state_types_accepted")
    test_valid_qutrit_and_qudit_registers_accepted()
    print("PASS test_valid_qutrit_and_qudit_registers_accepted")
    test_qudit_zero_dimension_is_local_dimension_type_error()
    print("PASS test_qudit_zero_dimension_is_local_dimension_type_error")
    test_qudit_register_nonpositive_shape_is_error()
    print("PASS test_qudit_register_nonpositive_shape_is_error")
    test_qudit_arity_mismatch_is_local_dimension_type_error()
    print("PASS test_qudit_arity_mismatch_is_local_dimension_type_error")
    test_qudit_register_arity_mismatch_is_error()
    print("PASS test_qudit_register_arity_mismatch_is_error")
    test_ebnf_documents_qutrit_qudit_types()
    print("PASS test_ebnf_documents_qutrit_qudit_types")
    print("OK - LISS-0074 Slice A")


if __name__ == "__main__":
    main()
