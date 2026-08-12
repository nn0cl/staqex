"""AT-TDD Phase 1 Red: LISS-0112 Slice B — Identity evolve / apply(I) on D=3."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source
from compiler.staqex.run import run_source

KET = ">"
UNSUPPORTED = "UNSUPPORTED_LOCAL_DIMENSION"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def _run_codes(result) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in result.diagnostics}


def test_apply_identity_on_qutrit_preserves_ket2() -> None:
    """apply(I) on State<Qutrit> |2⟩ must run (Identity no-op; LISS-0239)."""
    source = f"""
    package t
    pub fn main() -> Unit {{
        State<Qutrit> s = |2{KET}
        State out = apply(I, s)
        measure out
    }}
    """
    compiled = compile_source(source)
    assert UNSUPPORTED not in _codes(compiled), compiled.diagnostics
    assert compiled.ok, compiled.diagnostics

    result = run_source(source, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert UNSUPPORTED not in _run_codes(result), result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 2


def test_evolve_identity_on_qudit3_preserves_ket1() -> None:
    """evolve under I on State<Qudit<3>> must succeed with Hilbert dim 3 preserved."""
    source = f"""
    package t
    pub fn main() -> Unit {{
        State<Qudit<3>> s = |1{KET}
        State s = evolve {{ s under I for 0.0.s }}.run()
        measure s
    }}
    """
    compiled = compile_source(source)
    assert UNSUPPORTED not in _codes(compiled), compiled.diagnostics
    assert compiled.ok, compiled.diagnostics

    result = run_source(source, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert UNSUPPORTED not in _run_codes(result), result.diagnostics
    assert result.eval is not None and result.eval.joint.worlds
    values = {world.assign.get("s") for world in result.eval.joint.worlds}
    assert values == {1}, values


def test_apply_hadamard_on_qutrit_remains_unsupported() -> None:
    """Non-Identity operators stay fail-closed on D=3 (Slice B Identity-only)."""
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


def test_apply_identity_on_qudit4_remains_unsupported() -> None:
    """Slice B lifts D=3 only; Identity on Qudit<4> stays unsupported."""
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qudit<4>> s = |0{KET}
            State out = apply(I, s)
            measure out
        }}
        """
    )

    assert UNSUPPORTED in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_qubit_apply_identity_unchanged() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qubit> s = |0{KET}
            State out = apply(I, s)
            measure out
        }}
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert UNSUPPORTED not in _codes(compiled)


def main() -> None:
    test_apply_identity_on_qutrit_preserves_ket2()
    print("PASS test_apply_identity_on_qutrit_preserves_ket2")
    test_evolve_identity_on_qudit3_preserves_ket1()
    print("PASS test_evolve_identity_on_qudit3_preserves_ket1")
    test_apply_hadamard_on_qutrit_remains_unsupported()
    print("PASS test_apply_hadamard_on_qutrit_remains_unsupported")
    test_apply_identity_on_qudit4_remains_unsupported()
    print("PASS test_apply_identity_on_qudit4_remains_unsupported")
    test_qubit_apply_identity_unchanged()
    print("PASS test_qubit_apply_identity_unchanged")
    print("OK - LISS-0112 Slice B Phase 1 Red")


if __name__ == "__main__":
    main()
