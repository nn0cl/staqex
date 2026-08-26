"""AT-TDD Phase 1 Red: LISS-0074 Slice E — QASM/QPU qudit hard reject."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter
from compiler.staqex.cli import main as cli_main
from compiler.staqex.pipeline import compile_source
from compiler.staqex import run as run_mod

KET = ">"
UNSUPPORTED = "UNSUPPORTED_LOCAL_DIMENSION"


def _emit(source: str):
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    return QASM3Emitter(route=False).emit_unit(compiled.unit)


def test_run_hard_codes_include_unsupported_local_dimension() -> None:
    """CLI emit-qasm gates on run.HARD_CODES; Slice D code must be listed."""
    assert UNSUPPORTED in run_mod.HARD_CODES
    assert "LOCAL_DIMENSION_TYPE_ERROR" in run_mod.HARD_CODES


def test_cli_emit_qasm_rejects_qutrit_measure() -> None:
    source = f"""
    package t
    pub fn main() -> Unit {{
        State<Qutrit> s = |0{KET}
        Measure s
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


def test_emitter_rejects_annotation_only_qutrit_state() -> None:
    """Unused State<Qutrit> must not lower to qubit OPENQASM."""
    source = f"""
    package t
    pub fn main() -> Unit {{
        State<Qutrit> s = |0{KET}
        State observed = Coin()
        Measure observed
    }}
    """
    emitted = _emit(source)

    assert emitted.ok is False
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == UNSUPPORTED
    assert emitted.qasm == ""


def test_emitter_rejects_qutrit_register_program() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QutritRegister<1> r = system()
        State observed = Coin()
        Measure observed
    }
    """
    emitted = _emit(source)

    assert emitted.ok is False
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == UNSUPPORTED
    assert emitted.qasm == ""


def test_cli_emit_qasm_qubit_measure_unchanged() -> None:
    source = f"""
    package t
    pub fn main() -> Unit {{
        State<Qubit> s = |0{KET}
        Measure s
    }}
    """
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "qubit.sqx"
        path.write_text(source, encoding="utf-8")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = cli_main(["emit-qasm", str(path)])

    assert exit_code == 0, stdout.getvalue()
    assert "OPENQASM" in stdout.getvalue()


def main() -> None:
    test_run_hard_codes_include_unsupported_local_dimension()
    print("PASS test_run_hard_codes_include_unsupported_local_dimension")
    test_cli_emit_qasm_rejects_qutrit_measure()
    print("PASS test_cli_emit_qasm_rejects_qutrit_measure")
    test_emitter_rejects_annotation_only_qutrit_state()
    print("PASS test_emitter_rejects_annotation_only_qutrit_state")
    test_emitter_rejects_qutrit_register_program()
    print("PASS test_emitter_rejects_qutrit_register_program")
    test_cli_emit_qasm_qubit_measure_unchanged()
    print("PASS test_cli_emit_qasm_qubit_measure_unchanged")
    print("OK - LISS-0074 Slice E Phase 1 Red")


if __name__ == "__main__":
    main()
