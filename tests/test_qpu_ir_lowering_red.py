"""AT-TDD Phase 1 Red contract for LISS-0041 / ADR 0085."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _compile(source: str):
    result = compile_source(source)
    assert result.unit is not None, result.diagnostics
    return result


def test_static_register_exposes_immutable_qpu_program_metadata_and_nodes() -> None:
    result = _compile(
        """
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
    )

    ir = result.qpu_ir
    assert ir["kind"] == "ProviderNeutralQpuIR"
    assert "hilbert_shape" in ir
    assert "instructions" in ir
    assert isinstance(ir["instructions"], tuple)
    assert all(node.provenance for node in ir["instructions"])


def test_param_remains_symbolic_in_qpu_ir_without_host_binding() -> None:
    result = _compile(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<1> reg = system()
            Param<Angle> theta = parameter("theta")
            forEach q in reg {
                apply(Rz(theta), q)
            }
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert result.qpu_ir["parameters"] == [{"name": "theta", "domain": "Angle"}]
    assert "Host" not in repr(result.qpu_ir["parameters"])


def test_terminal_measurement_is_an_ir_node_not_a_provider_operation() -> None:
    result = _compile(
        """
        package t
        pub fn main() -> Unit {
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    measurement = result.qpu_ir["measurement"]
    assert measurement["terminal"] is True
    assert measurement.get("operation") == "Measure"
    assert "submit" not in repr(measurement).lower()


def test_unsupported_dynamic_capability_is_a_hard_diagnostic_without_host_fallback() -> None:
    result = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = dirac(0)
            State evolved = evolve { psi under X for 1 until converged(psi) max 64 }.run()
            measure evolved
        }
        """
    )

    assert any(
        diagnostic.get("code") == "E_QPU_UNSUPPORTED_CAPABILITY"
        for diagnostic in result.diagnostics
    )
    assert "Host" not in repr(result.qpu_ir)


def test_qpu_ir_has_no_provider_sdk_or_serialization_boundary() -> None:
    result = _compile(
        """
        package t
        pub fn main() -> Unit {
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    rendered = repr(result.qpu_ir).lower()
    assert "braket" not in rendered
    assert "qiskit" not in rendered
    assert "json" not in rendered
