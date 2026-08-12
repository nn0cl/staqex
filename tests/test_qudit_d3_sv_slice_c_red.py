"""AT-TDD Phase 1 Red: LISS-0112 Slice C — conformance/catalog closeout."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import main as cli_main
from compiler.staqex.pipeline import compile_source

KET = ">"
UNSUPPORTED = "UNSUPPORTED_LOCAL_DIMENSION"

_CONFORMANCE = (
    _REPO / "docs" / "specs" / "staqex-v1-conformance-scenario-catalog.md"
)
_DIAGNOSTIC = _REPO / "docs" / "specs" / "staqex-v1-diagnostic-catalog.md"


def _codes(compiled) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compiled.diagnostics}


def test_conformance_catalog_lists_d3_sv_mvp() -> None:
    """E06-003 must cover Kernel D=3 measure + Identity (LISS-0112 A/B)."""
    text = _CONFORMANCE.read_text(encoding="utf-8")
    assert "E06-003" in text, "missing E06-003 row for LISS-0112 D=3 SV MVP"
    assert "LISS-0112" in text
    assert "test_qudit_d3_sv_slice_a_red.py" in text
    assert "test_qudit_d3_sv_slice_b_red.py" in text


def test_diagnostic_catalog_notes_liss0112_lift_surfaces() -> None:
    """UNSUPPORTED_LOCAL_DIMENSION docs must cite LISS-0112 lift surfaces."""
    text = _DIAGNOSTIC.read_text(encoding="utf-8")
    assert "LISS-0112" in text, "diagnostic catalog must reference LISS-0112"
    # Kernel meaning row should still name the code and QASM appendix reuse.
    assert UNSUPPORTED in text


def test_qasm_emit_still_rejects_qutrit_measure() -> None:
    """Closeout must not weaken LISS-0074 QASM hard reject."""
    source = f"""
    package t
    pub fn main() -> Unit {{
        State<Qutrit> s = |0{KET}
        measure s
    }}
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "qutrit.sqx"
        path.write_text(source, encoding="utf-8")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = cli_main(["emit-qasm", str(path)])

    assert exit_code != 0
    assert "OPENQASM" not in stdout.getvalue()


def test_qudit4_measure_remains_unsupported() -> None:
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            State<Qudit<4>> s = |0{KET}
            measure s
        }}
        """
    )

    assert UNSUPPORTED in _codes(compiled), compiled.diagnostics
    assert not compiled.ok


def test_apply_hadamard_on_qutrit_remains_unsupported() -> None:
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


def main() -> None:
    test_conformance_catalog_lists_d3_sv_mvp()
    print("PASS test_conformance_catalog_lists_d3_sv_mvp")
    test_diagnostic_catalog_notes_liss0112_lift_surfaces()
    print("PASS test_diagnostic_catalog_notes_liss0112_lift_surfaces")
    test_qasm_emit_still_rejects_qutrit_measure()
    print("PASS test_qasm_emit_still_rejects_qutrit_measure")
    test_qudit4_measure_remains_unsupported()
    print("PASS test_qudit4_measure_remains_unsupported")
    test_apply_hadamard_on_qutrit_remains_unsupported()
    print("PASS test_apply_hadamard_on_qutrit_remains_unsupported")
    print("OK - LISS-0112 Slice C Phase 1 Red")


if __name__ == "__main__":
    main()
