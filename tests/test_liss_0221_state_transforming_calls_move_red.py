"""AT-TDD Phase 1 Red: LISS-0221 — transforming Calls move linear args."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def _messages(diags: list[dict]) -> str:
    return "; ".join(
        f"{d.get('code')}:{d.get('message')}" for d in diags
    )


def test_lindblad_moves_input_rho() -> None:
    """Transformation consumes rho; Measure evolved discharges the result."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            DensityState<Qubit> rho = DensityState(Ensemble([(1.0, |0>)]))
            Operator H = Z
            Operator jumps = X
            Float t = 0.1
            DensityState<Qubit> evolved = lindblad(rho, H, jumps, t)
            Measure evolved
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(compiled.diagnostics), (
        f"lindblad must move rho; got {_messages(compiled.diagnostics)}"
    )
    assert compiled.ok, compiled.diagnostics


def test_expect_does_not_move_argument() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Qubit> q = |0>
            Float e = expect(Z, q)
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(compiled.diagnostics), (
        f"expect must leave q live; got {_messages(compiled.diagnostics)}"
    )


def test_inner_does_not_move_arguments() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Qubit> a = |0>
            State<Qubit> b = |1>
            Float ov = inner(a, b)
        }
        """
    )
    codes = _codes(compiled.diagnostics)
    assert "LINEAR_IMPLICIT_DISCARD" in codes, (
        f"inner must leave a/b live; got {_messages(compiled.diagnostics)}"
    )


def test_same_name_hadamard_rebind_emits_discard_without_measure() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            State<Int> q = hadamard(q)
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(compiled.diagnostics), (
        f"fresh obligation after rebind must discard; got "
        f"{_messages(compiled.diagnostics)}"
    )


def test_same_name_hadamard_rebind_then_measure_ok() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            State<Int> q = hadamard(q)
            Measure q
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" not in _codes(compiled.diagnostics)
    assert "LINEAR_DUPLICATE_USE" not in _codes(compiled.diagnostics)
    assert compiled.ok, compiled.diagnostics


def main() -> None:
    test_lindblad_moves_input_rho()
    print("PASS test_lindblad_moves_input_rho")
    test_expect_does_not_move_argument()
    print("PASS test_expect_does_not_move_argument")
    test_inner_does_not_move_arguments()
    print("PASS test_inner_does_not_move_arguments")
    test_same_name_hadamard_rebind_emits_discard_without_measure()
    print("PASS test_same_name_hadamard_rebind_emits_discard_without_measure")
    test_same_name_hadamard_rebind_then_measure_ok()
    print("PASS test_same_name_hadamard_rebind_then_measure_ok")
    print("OK - LISS-0221 Phase 1 Red")


if __name__ == "__main__":
    main()
