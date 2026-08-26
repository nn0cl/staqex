"""Phase 2 Green checks for the immutable QPU IR lowering slice."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_openqasm_adapter_consumes_qpu_ir_in_memory() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics

    emitted = QASM3Emitter(route=False).emit_qpu_program(compiled.qpu_ir)
    assert emitted.ok, emitted.notes
    assert "h q[0];" in emitted.qasm
    assert "measure q[0]" in emitted.qasm  # OpenQASM3 output keyword, always lowercase


def test_qpu_program_root_is_immutable_and_preserves_node_provenance() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            ForEach q in reg {
                apply(H, q)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok
    program = compiled.qpu_ir
    assert type(program).__name__ == "QpuProgram"
    assert program["instructions"][0].provenance["source"] == "ForEach.apply"

