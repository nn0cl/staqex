"""Phase 1 Red contracts for LISS-0067 / ADR 0105.

These tests describe the accepted multi-register boundary. They are expected
to fail until the parser, type checker, and QPU IR mapping implement the
reviewed contract. No provider or physical-routing behavior is tested here.
"""

from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {item.get("code", "") for item in compile_source(source).diagnostics}


def _bell_pair_source(operator: str) -> str:
    return f"""
package multi_register
system BellPair {{
    register data : QubitRegister<2>
    register ancilla : QubitRegister<1>
}}
pub fn main() -> Unit {{
    Operator<RegisterSet<BellPair>> H = {operator}
    State<Qubit> psi = |0>
    Measure psi
}}
"""


def test_named_register_shape_is_a_static_composite_acting_space() -> None:
    result = compile_source(_bell_pair_source("I"))

    assert result.ok, result.diagnostics
    assert result.qpu_ir["hilbert_shape"] == {
        "logical_qubits": 3,
        "hilbert_dimension": 8,
    }


def test_qualified_sites_preserve_the_composite_operator_type() -> None:
    result = compile_source(_bell_pair_source("Z[data[0]] * Z[ancilla[0]]"))

    assert result.ok, result.diagnostics
    assert result.qpu_ir["acting_space"] == "RegisterSet<BellPair>"


def test_qpu_ir_keeps_register_local_and_flat_identity() -> None:
    result = compile_source(_bell_pair_source("Z[data[0]] * Z[ancilla[0]]"))

    assert result.ok, result.diagnostics
    assert result.qpu_ir["logical_registers"] == [
        {"name": "data", "width": 2, "offset": 0},
        {"name": "ancilla", "width": 1, "offset": 2},
    ]
    assert result.qpu_ir["tensor_order"] == ["data", "ancilla"]
    assert result.qpu_ir["tensor_order_provenance"] == {
        "source": "system register declaration order",
        "registers": ["data", "ancilla"],
    }


def test_unqualified_site_is_rejected_in_a_multi_register_context() -> None:
    diagnostics = _codes(_bell_pair_source("Z[0]"))

    assert "MULTI_REGISTER_INDEX_AMBIGUOUS" in diagnostics, diagnostics


def test_incompatible_single_register_operator_is_not_implicitly_lifted() -> None:
    source = """
package multi_register
system BellPair {
    register data : QubitRegister<2>
    register ancilla : QubitRegister<1>
}
pub fn make_operator() -> Operator<QubitRegister<2>> {
    return Z[0]
}
pub fn main() -> Unit {
    Operator<RegisterSet<BellPair>> H = make_operator()
    State<Qubit> psi = |0>
    Measure psi
}
"""
    diagnostics = _codes(source)

    assert "ACTING_SPACE_MISMATCH" in diagnostics, diagnostics


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
