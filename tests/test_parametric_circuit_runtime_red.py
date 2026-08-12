"""AT-TDD: LISS-0027 parametric QPU IR, OpenQASM, and Host binding validation."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.parametric_binding import (  # noqa: E402
    PARAM_BINDING_MISSING,
    PARAM_BINDING_UNKNOWN,
    PARAM_BINDING_VALUE_ERROR,
    extract_circuit_parameters,
    validate_parameter_bindings,
)
from compiler.staqex.pipeline import compile_source  # noqa: E402


_PARAM_PROGRAM = """
package t
pub fn main() -> Unit {
    QubitRegister<1> reg = system()
    Param<Angle> theta = parameter("theta")
    ForEach q in reg {
        apply(Rz(theta), q)
    }
    State<Int> observed = Coin()
    Measure observed
}
"""


def _compile(source: str = _PARAM_PROGRAM):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    return compiled


def test_openqasm_declares_symbolic_circuit_parameters() -> None:
    compiled = _compile()
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert emitted.ok, emitted.notes
    assert "input float theta;" in emitted.qasm
    assert "rz(theta) q[0];" in emitted.qasm


def test_emit_unit_uses_qpu_ir_lane_for_parametric_static_register() -> None:
    compiled = _compile()
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)

    assert emitted.ok
    assert "rz(theta)" in emitted.qasm
    assert "c[0] = measure q[0];" in emitted.qasm  # OpenQASM3 output keyword, always lowercase


def test_concrete_bindings_substitute_symbolic_angles_in_openqasm() -> None:
    compiled = _compile()
    emitted = QASM3Emitter(route=False).emit_qpu_program(
        compiled.qpu_ir,
        parameter_values={"theta": 0.5},
    )

    assert emitted.ok, emitted.notes
    assert "input float theta;" not in emitted.qasm
    assert "rz(0.5) q[0];" in emitted.qasm


def test_host_binding_validation_requires_all_declared_parameters() -> None:
    compiled = _compile()
    declared = extract_circuit_parameters(compiled.unit)

    codes = {
        diagnostic["code"]
        for diagnostic in validate_parameter_bindings(declared, {})
    }

    assert PARAM_BINDING_MISSING in codes


def test_host_binding_rejects_unknown_parameters() -> None:
    compiled = _compile()
    declared = extract_circuit_parameters(compiled.unit)

    codes = {
        diagnostic["code"]
        for diagnostic in validate_parameter_bindings(
            declared, {"theta": 0.5, "phi": 0.1}
        )
    }

    assert PARAM_BINDING_UNKNOWN in codes


def test_host_binding_rejects_non_finite_angle_values() -> None:
    compiled = _compile()
    declared = extract_circuit_parameters(compiled.unit)

    codes = {
        diagnostic["code"]
        for diagnostic in validate_parameter_bindings(
            declared, {"theta": float("nan")}
        )
    }

    assert PARAM_BINDING_VALUE_ERROR in codes


def test_binding_key_uses_parameter_literal_not_only_local_name() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            Param<Angle> phi = parameter("theta")
            ForEach q in reg {
                apply(Rz(phi), q)
            }
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.qpu_ir["parameters"] == [{"name": "theta", "domain": "Angle"}]
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert "rz(theta)" in emitted.qasm


if __name__ == "__main__":
    for test in (
        test_openqasm_declares_symbolic_circuit_parameters,
        test_emit_unit_uses_qpu_ir_lane_for_parametric_static_register,
        test_concrete_bindings_substitute_symbolic_angles_in_openqasm,
        test_host_binding_validation_requires_all_declared_parameters,
        test_host_binding_rejects_unknown_parameters,
        test_host_binding_rejects_non_finite_angle_values,
        test_binding_key_uses_parameter_literal_not_only_local_name,
    ):
        test()
    print("OK — parametric circuit runtime tests")
