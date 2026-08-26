"""AT-TDD Phase 1 Red: LISS-0112 Slice A — D=3 ket + Measure SV path."""

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


def test_qutrit_basis_kets_measure_without_unsupported() -> None:
    """D=3 SV must accept |0⟩…|2⟩ on State<Qutrit> (lift Slice D reject)."""
    for label in ("0", "1", "2"):
        source = f"""
        package t
        pub fn main() -> Unit {{
            State<Qutrit> s = |{label}{KET}
            Measure s
        }}
        """
        compiled = compile_source(source)
        assert UNSUPPORTED not in _codes(compiled), (label, compiled.diagnostics)
        assert compiled.ok, (label, compiled.diagnostics)

        result = run_source(source, seed=0, stdout=io.StringIO())
        assert result.compile_ok, (label, result.diagnostics)
        assert UNSUPPORTED not in _run_codes(result), (label, result.diagnostics)
        assert result.eval is not None and result.eval.joint.worlds
        values = {world.assign.get("s") for world in result.eval.joint.worlds}
        assert values == {int(label)}, (label, values)


def test_qudit3_ket2_measure_accepted() -> None:
    """|2⟩ distinguishes dim-3 from qubit SV (which cannot host label 2)."""
    source = f"""
    package t
    pub fn main() -> Unit {{
        State<Qudit<3>> s = |2{KET}
        Measure s
    }}
    """
    compiled = compile_source(source)
    assert UNSUPPORTED not in _codes(compiled), compiled.diagnostics
    assert compiled.ok, compiled.diagnostics

    result = run_source(source, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval is not None and result.eval.joint.worlds
    values = {world.assign.get("s") for world in result.eval.joint.worlds}
    assert values == {2}, values


def test_qudit4_measure_remains_unsupported() -> None:
    """Slice A lifts D=3 only; other local dims stay fail-closed."""
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qudit<4>> s = |0{KET}
            Measure s
        }}
        """
    )

    assert UNSUPPORTED in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_qutrit_out_of_range_ket_still_local_dimension_type_error() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qutrit> s = |3{KET}
            Measure s
        }}
        """
    )

    assert "LOCAL_DIMENSION_TYPE_ERROR" in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_qubit_measure_unchanged() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qubit> s = |0{KET}
            Measure s
        }}
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert UNSUPPORTED not in _codes(compiled)


def main() -> None:
    test_qutrit_basis_kets_measure_without_unsupported()
    print("PASS test_qutrit_basis_kets_measure_without_unsupported")
    test_qudit3_ket2_measure_accepted()
    print("PASS test_qudit3_ket2_measure_accepted")
    test_qudit4_measure_remains_unsupported()
    print("PASS test_qudit4_measure_remains_unsupported")
    test_qutrit_out_of_range_ket_still_local_dimension_type_error()
    print("PASS test_qutrit_out_of_range_ket_still_local_dimension_type_error")
    test_qubit_measure_unchanged()
    print("PASS test_qubit_measure_unchanged")
    print("OK - LISS-0112 Slice A Phase 1 Red")


if __name__ == "__main__":
    main()
