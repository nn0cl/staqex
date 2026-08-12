"""AT-TDD Phase 1 Red: LISS-0019 provider-neutral QPU IR projection."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _qpu_ir(source: str):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    return getattr(compiled, "qpu_ir", None)


def test_qpu_ir_projection_preserves_provenance_and_terminal_measurement() -> None:
    ir = _qpu_ir(
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

    assert ir is not None
    assert "provenance" in ir
    assert "measurement" in ir
    assert ir["measurement"]["terminal"] is True


def test_qpu_ir_keeps_param_symbolic_without_host_binding() -> None:
    ir = _qpu_ir(
        """
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
    )

    assert ir is not None
    assert ir["parameters"] == [{"name": "theta", "domain": "Angle"}]
    assert "Host" not in repr(ir["parameters"])


def test_qpu_ir_projection_has_no_provider_submission_objects() -> None:
    ir = _qpu_ir(
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

    assert ir is not None
    rendered = repr(ir)
    assert "braket" not in rendered.lower()
    assert "qiskit" not in rendered.lower()
    assert "submit" not in rendered.lower()


if __name__ == "__main__":
    for test in (
        test_qpu_ir_projection_preserves_provenance_and_terminal_measurement,
        test_qpu_ir_keeps_param_symbolic_without_host_binding,
        test_qpu_ir_projection_has_no_provider_submission_objects,
    ):
        test()
    print("OK — QPU IR boundary Red tests")
