"""LISS-0440 Phase 1 Red: namespace declarations do not become execution."""

from __future__ import annotations

from compiler.staqex.pipeline import compile_source


def _codes(source: str) -> set[str]:
    return {str(d.get("code", "")) for d in compile_source(source).diagnostics}


def test_namespace_declarations_leave_compilation_unit_main_as_entry() -> None:
    source = """
package t
namespace Topology.SSH {
  pub struct Params { pub val coupling: Float }
}
pub fn main() -> Unit {
  Topology.SSH.Params p = Topology.SSH.Params(1.0)
  State psi = |0>
  Measure psi
}
"""
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    assert "TOPLEVEL_EXECUTION_ERROR" not in codes, codes


def test_namespace_executable_member_is_rejected_before_execution() -> None:
    source = """
package t
namespace NotAProgram {
  H(q)
}
pub fn main() -> Unit {
  State psi = |0>
  Measure psi
}
"""
    codes = _codes(source)
    assert "PARSE_ERROR" in codes, codes
    assert "TOPLEVEL_EXECUTION_ERROR" not in codes, codes
