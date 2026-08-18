"""LISS-0441 Phase 1 Red: source roles stay visible at the existing bridges."""

from __future__ import annotations

from compiler.staqex.pipeline import compile_source


def _codes(source: str) -> set[str]:
    return {str(d.get("code", "")) for d in compile_source(source).diagnostics}


def test_classical_coefficient_and_quantum_state_are_distinct_in_source() -> None:
    source = """
package t
pub fn main() -> Unit {
  Float coupling = 1.0
  Operator H = coupling * X
  State psi = |0>
  State psi = Evolve { psi under H for 0.1.fs using Suzuki(order = 2, steps = 2) }.run()
  Measure psi
}
"""
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    assert "TOPLEVEL_EXECUTION_ERROR" not in codes, codes


def test_realization_is_not_implicit_in_a_namespace_or_host_block() -> None:
    source = """
package t
namespace Physics {
  pub struct Hamiltonian { pub val scale: Float }
}
pub fn main() -> Unit {
  Physics.Hamiltonian h = Physics.Hamiltonian(1.0)
  State psi = |0>
  Measure psi
}
"""
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    assert "REALIZE_IMPLICIT_CONVERSION" not in codes, codes
