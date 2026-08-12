"""AT-TDD Phase 1 Red: LISS-0049 QASM function-call lowering boundary.

Reproduces the gap recorded in
docs/issues/LISS-0049-qasm-function-call-lowering.md: `emit-qasm` on a
program whose `main` calls a Measure-free `fn` silently substitutes the
empty-program fallback (`h; Measure`) instead of rejecting the program.
This pins the Architecture Path decision (2026-07-25, Option B): reject
with `QASM_FUNCTION_CALL_UNSUPPORTED` and actionable advice, and never emit
a silently wrong circuit in its place.

Expected to fail until Phase 2 Green implements the rejection.
"""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.cli import main as cli_main  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402

_FUNCTION_CALL_SOURCE = """
package t
fn origin() -> State<Int> {
    return Dirac(0)
}
pub fn main() -> Unit {
    State<Int> result = origin()
    Measure result
}
"""

_DIAGNOSTIC_CODE = "QASM_FUNCTION_CALL_UNSUPPORTED"
_DIAGNOSTIC_MESSAGE = (
    "Emitting QASM for function calls is currently unsupported. "
    "Please inline the function logic manually."
)


def _emit(source: str):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    return QASM3Emitter(route=False).emit_unit(compiled.unit)


def test_qasm_function_call_is_rejected_not_silently_faked() -> None:
    emitted = _emit(_FUNCTION_CALL_SOURCE)

    assert emitted.ok is False
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == _DIAGNOSTIC_CODE


def test_qasm_function_call_rejection_carries_actionable_message() -> None:
    emitted = _emit(_FUNCTION_CALL_SOURCE)

    assert any(_DIAGNOSTIC_MESSAGE in note for note in emitted.notes), emitted.notes


def test_qasm_function_call_rejection_never_emits_the_empty_program_fallback() -> None:
    emitted = _emit(_FUNCTION_CALL_SOURCE)

    assert emitted.qasm == ""
    gates = emitted.circuit.gates if emitted.circuit is not None else []
    assert not any(g.comment == "empty program fallback" for g in gates)


def test_cli_emit_qasm_exits_nonzero_and_prints_no_fabricated_qasm() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        src_path = Path(tmp) / "liss0049.sqx"
        src_path.write_text(_FUNCTION_CALL_SOURCE, encoding="utf-8")

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = cli_main(["emit-qasm", str(src_path)])

        assert exit_code == 1
        assert stdout.getvalue().strip() == ""


if __name__ == "__main__":
    tests = [
        test_qasm_function_call_is_rejected_not_silently_faked,
        test_qasm_function_call_rejection_carries_actionable_message,
        test_qasm_function_call_rejection_never_emits_the_empty_program_fallback,
        test_cli_emit_qasm_exits_nonzero_and_prints_no_fabricated_qasm,
    ]
    for test in tests:
        test()
    print("OK — qasm function-call rejection tests")
