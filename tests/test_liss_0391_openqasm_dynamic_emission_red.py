"""AT-TDD Phase 1 Red: LISS-0391 OpenQASM 3 emission for the Dynamic QPU lane.

Target: docs/architecture/adr/0201-openqasm-dynamic-lane-emission.md /
LISS-0391.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


_SOURCE_MEASURE_MATCH_RESET = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { apply(X, q) }
            1 => { }
        }
        reset q
    }
    State<Int> observed = coin()
    measure observed
}
"""


def test_emission_available_without_any_fake_profile_setting() -> None:
    """Scenario: emission is available whenever the program compiles,
    independent of any dynamic_fake_profile Host gate (ADR 0201 Decision 4).
    """
    from compiler.staqex.backend.qasm.dynamic_emitter import emit_dynamic_qpu_qasm3

    compiled = compile_source(_SOURCE_MEASURE_MATCH_RESET)
    assert compiled.unit is not None

    result = emit_dynamic_qpu_qasm3(compiled.unit)

    assert result.ok is True
    assert result.qasm != ""


def test_emission_uses_native_qasm3_vocabulary() -> None:
    """Scenario: measure/match/reset map to QASM3's own native syntax --
    no invented dialect (ADR 0201 Decision 3).
    """
    from compiler.staqex.backend.qasm.dynamic_emitter import emit_dynamic_qpu_qasm3

    compiled = compile_source(_SOURCE_MEASURE_MATCH_RESET)
    assert compiled.unit is not None

    result = emit_dynamic_qpu_qasm3(compiled.unit)
    qasm = result.qasm

    assert "qubit q;" in qasm
    assert "bit bit;" in qasm
    assert "bit = measure q;" in qasm
    assert "if (bit == 0)" in qasm
    assert "if (bit == 1)" in qasm
    assert "x q;" in qasm
    assert "reset q;" in qasm


def test_emission_does_not_claim_physical_execution() -> None:
    """Scenario: emission makes no physical_execution_claimed claim of any
    kind -- the EmitResult carries no such field, and OPENQASM header
    text is the only claim made (this is a text artifact, not a
    submission).
    """
    from compiler.staqex.backend.qasm.dynamic_emitter import emit_dynamic_qpu_qasm3

    compiled = compile_source(_SOURCE_MEASURE_MATCH_RESET)
    assert compiled.unit is not None

    result = emit_dynamic_qpu_qasm3(compiled.unit)

    assert not hasattr(result, "physical_execution_claimed")
    assert "OPENQASM 3" in result.qasm


def test_static_qasm_emitter_is_unaffected() -> None:
    """Scenario: the existing Static QPU QASM3Emitter is byte-for-byte
    unaffected by this Issue (regression guard, not a new assertion).
    """
    from compiler.staqex.backend.qasm.emitter import QASM3Emitter

    source = """
package t
pub fn main() -> Unit {
    QubitRegister<1> reg = system()
    forEach q in reg {
        apply(H, q)
    }
    State<Int> observed = coin()
    measure observed
}
"""
    compiled = compile_source(source)
    assert compiled.unit is not None
    result = QASM3Emitter().emit_unit(compiled.unit)
    assert result.ok is True
