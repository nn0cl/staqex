"""Acceptance contracts for LISS-0058 acting-space typing.

These tests preserve the semantic boundary selected by ADR 0102: declared
single-register shape is authoritative, and context-free execution never
falls back to a guessed one-qubit space.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {item.get("code", "") for item in compile_source(source).diagnostics}


def _program(operator: str, *, register: int = 4) -> str:
    return f"""
package acting_space
pub fn main() -> Unit {{
    QubitRegister<{register}> register = system()
    Operator<QubitRegister<{register}>> H = {operator}
    State<Qubit> a = |0>
    State<Qubit> b = |0>
    state b = |0>
    State<Qubit> c = |0>
    state c = |0>
    State<Qubit> d = |0>
    state d = |0>
    state (a, b, c, d) = evolve {{ (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 1) }}.run()
    state b = |0>
    state c = |0>
    state d = |0>
    measure a
}}
"""


def test_site_free_identity_uses_declared_register_shape() -> None:
    source = _program("sum (i in Index<3..1>) { Z[i] }")
    compiled = compile_source(source)

    assert compiled.ok, compiled.diagnostics
    assert compiled.qpu_ir.values["hilbert_shape"]["logical_qubits"] == 4


def test_identity_only_operator_does_not_infer_a_smaller_space() -> None:
    source = _program("1.0545718e-19 * I")
    result = run_source(source, seed=0, stdout=io.StringIO())

    assert result.compile_ok, result.diagnostics
    assert result.eval.joint.worlds
    assert {len(world.assign) for world in result.eval.joint.worlds} == {4}


def test_declared_shape_is_retained_when_high_qubits_are_unused() -> None:
    source = _program("1.0545718e-19 * Z[0]")
    result = run_source(source, seed=0, stdout=io.StringIO())

    assert result.compile_ok, result.diagnostics
    assert result.eval.joint.worlds
    assert {len(world.assign) for world in result.eval.joint.worlds} == {4}


def test_operator_return_keeps_its_acting_space_across_function_boundary() -> None:
    source = """
package acting_space
fn make_h() -> Operator<QubitRegister<4>> {
    return 1.0545718e-19 * Z[0]
}
pub fn main() -> Unit {
    QubitRegister<4> register = system()
    Operator<QubitRegister<4>> H = make_h()
    State<Qubit> a = |0>
    State<Qubit> b = |0>
    State<Qubit> c = |0>
    State<Qubit> d = |0>
    state (a, b, c, d) = evolve { (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 1) }.run()
    state b = |0>
    state c = |0>
    state d = |0>
    measure a
}
"""
    result = run_source(source, seed=0, stdout=io.StringIO())

    assert result.compile_ok, result.diagnostics
    assert result.eval.joint.worlds
    assert {len(world.assign) for world in result.eval.joint.worlds} == {4}


def test_context_free_operator_execution_has_no_one_qubit_fallback() -> None:
    source = """
package acting_space
pub fn main() -> Unit {
    Operator H = I
    state psi = |0>
    state out = evolve { psi under H for 0.1 using Suzuki(order = 2, steps = 1) }.run()
    state psi = |0>
    measure out
}
"""
    result = run_source(source, seed=0, stdout=io.StringIO())

    assert not result.compile_ok
    assert "ACTING_SPACE_UNDETERMINED" in _codes(source) or any(
        "ACTING_SPACE_UNDETERMINED" in item.get("code", "")
        for item in result.diagnostics
    )


def test_multi_register_operator_is_rejected_explicitly() -> None:
    source = """
package acting_space
pub fn main() -> Unit {
    QubitRegister<2> left = system()
    QubitRegister<2> right = system()
    Operator<QubitRegister<2> * QubitRegister<2>> H = Z[0] * Z[1]
    state psi = |00>
    state out = evolve { psi under H for 0.1 using Suzuki(order = 2, steps = 1) }.run()
    state psi = |0>
    measure out
}
"""
    diagnostics = _codes(source)

    assert "PARSE_ERROR" in diagnostics or any(
        "MULTI_REGISTER" in code or "ACTING_SPACE" in code for code in diagnostics
    ), diagnostics


if __name__ == "__main__":
    _failed = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
            except AssertionError as _error:
                _failed += 1
                print(f"FAIL: {_name}: {_error}")
            else:
                print(f"PASS {_name}")
    raise SystemExit(1 if _failed else 0)
