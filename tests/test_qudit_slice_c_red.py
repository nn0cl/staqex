"""AT-TDD Phase 1 Red: LISS-0074 Slice C — qudit acting-space / no silent qubit coerce."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.finite_binder import (
    IDENTITY_ACTING_SPACE_UNDETERMINED,
    identity_acting_space_diagnostics,
)
from compiler.staqex.pipeline import compile_source

KET = ">"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def _identity_codes(compiled) -> set[str]:
    if compiled.unit is None:
        return set()
    return {
        diagnostic.get("code", "")
        for diagnostic in identity_acting_space_diagnostics(compiled.unit)
    }


def test_qutrit_register_identity_resolves_acting_space() -> None:
    """Declared QutritRegister must not fall through as undetermined qubit space."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator<QutritRegister<2>> H = I
            State observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert IDENTITY_ACTING_SPACE_UNDETERMINED not in _identity_codes(compiled), (
        _identity_codes(compiled)
    )


def test_silent_qubit_operator_on_qutrit_register_rejected() -> None:
    """Qutrit-only context must not accept Operator<QubitRegister<N>>."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QutritRegister<2> r = system()
            Operator<QubitRegister<2>> H = I
            State observed = Coin()
            Measure observed
        }
        """
    )

    codes = _codes(compiled)
    assert (
        "OPERATOR_DOMAIN_ERROR" in codes or "ACTING_SPACE_MISMATCH" in codes
    ), compiled.diagnostics
    assert not compiled.ok


def test_qubit_operator_return_not_assignable_to_qutrit_register() -> None:
    """Regression: QubitRegister ↛ QutritRegister at function boundary."""
    compiled = compile_source(
        """
        package t
        fn make() -> Operator<QubitRegister<2>> {
            return I
        }
        pub fn main() -> Unit {
            Operator<QutritRegister<2>> H = make()
            State observed = Coin()
            Measure observed
        }
        """
    )

    assert "OPERATOR_DOMAIN_ERROR" in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_qutrit_register_equiv_qudit_register_dim3() -> None:
    """QutritRegister<N> ≅ QuditRegister<3,N> for acting-space checks."""
    compiled = compile_source(
        """
        package t
        fn make() -> Operator<QutritRegister<2>> {
            return I
        }
        pub fn main() -> Unit {
            Operator<QuditRegister<3, 2>> H = make()
            State observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert "OPERATOR_DOMAIN_ERROR" not in _codes(compiled)


def test_typed_qubit_qutrit_product_accepted() -> None:
    """Typed mixed product must not coerce the Qutrit factor to Qubit."""
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qubit> q0 = |0{KET}
            State<Qutrit> t0 = |0{KET}
            State<(Qubit, Qutrit)> (q, t) = q0 *|* t0
            State observed = Coin()
            Measure observed
        }}
        """
    )

    # Type acceptance only — unused product factors may still LINEAR-discard.
    assert "OPERATOR_DOMAIN_ERROR" not in _codes(compiled)
    assert "PRODUCT_TYPE_MISMATCH" not in _codes(compiled)
    assert "PARSE_ERROR" not in _codes(compiled)


def main() -> None:
    test_qutrit_register_identity_resolves_acting_space()
    print("PASS test_qutrit_register_identity_resolves_acting_space")
    test_silent_qubit_operator_on_qutrit_register_rejected()
    print("PASS test_silent_qubit_operator_on_qutrit_register_rejected")
    test_qubit_operator_return_not_assignable_to_qutrit_register()
    print("PASS test_qubit_operator_return_not_assignable_to_qutrit_register")
    test_qutrit_register_equiv_qudit_register_dim3()
    print("PASS test_qutrit_register_equiv_qudit_register_dim3")
    test_typed_qubit_qutrit_product_accepted()
    print("PASS test_typed_qubit_qutrit_product_accepted")
    print("OK - LISS-0074 Slice C Phase 1 Red")


if __name__ == "__main__":
    main()
