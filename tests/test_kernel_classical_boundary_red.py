"""AT-TDD Phase 1 Red: LISS-0026 / ADR 0069.

These tests intentionally describe the accepted QPU-lane boundary before the
parser, elaborator, and diagnostics exist.  They are the reviewable Red
contract; implementation must not be added in this phase.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.codegen_qasm import OpenQASM3Generator  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_static_foreach_is_kernel_elaboration_and_emits_one_gate_per_wire() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> reg = system()
        ForEach q in reg {
            apply(H, q)
        }
        State<Int> answer = Coin()
        Measure answer
    }
    """

    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None

    qasm = OpenQASM3Generator(route=False).generate(compiled.unit)
    assert len(re.findall(r"(?m)^h q\[", qasm)) == 3


def test_foreach_element_is_opaque_and_cannot_become_an_int_index() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            QubitRegister<3> reg = system()
            ForEach q in reg {
                Int i = index(q)
                apply(H, q)
            }
            State<Int> answer = Coin()
            Measure answer
        }
        """
    )

    assert "QPU_CLASSICAL_CONTROL_ERROR" in codes


def test_measurement_dependent_foreach_bound_is_rejected_before_submission() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            State<Int> width = Coin()
            ForEach q in register(Measure width) {
                apply(H, q)
            }
            Measure width
        }
        """
    )

    assert "FOR_EACH_DYNAMIC_BOUND_ERROR" in codes


def test_host_value_cannot_be_declared_inside_qpu_kernel() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            Host<Float> temperature = host_input()
            State<Int> answer = Coin()
            Measure answer
        }
        """
    )

    assert "HOST_TYPE_IN_KERNEL_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_static_foreach_is_kernel_elaboration_and_emits_one_gate_per_wire,
        test_foreach_element_is_opaque_and_cannot_become_an_int_index,
        test_measurement_dependent_foreach_bound_is_rejected_before_submission,
        test_host_value_cannot_be_declared_inside_qpu_kernel,
    ):
        test()
    print("OK — Kernel classical boundary Red tests")
