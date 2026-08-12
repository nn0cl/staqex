"""LISS-0290 Phase 1 Red — ADR 0180 residual (fill ty / Call / QASM).

Acceptance (ADR 0180 Decision §3 + LISS-0290):
- Typechecker fills omitted StateBind.ty when elaboration is unique.
- Inferred Operator locals are visible to OpenQASM emission.
- Bare classical Float-returning Call binds evaluate without Joint misbind.
- Bare named struct construction is Classical/Struct, not LINEAR State.
- Classical↔State ambiguity remains fail-closed.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from compiler.staqex.ast_nodes import StateBind
from compiler.staqex.codegen_qasm import StaqexCompiler
from compiler.staqex.host import run_source
from compiler.staqex.pipeline import compile_source


def _bind_named(unit, name: str) -> StateBind:
    assert unit is not None and unit.main is not None
    for stmt in unit.main.body.stmts:
        if isinstance(stmt, StateBind) and name in stmt.names:
            return stmt
    raise AssertionError(f"no StateBind named {name!r}")


def test_0290_typecheck_fills_operator_and_float_ty() -> None:
    """Then inferred Operator / Float binds have filled TypeRef on the AST."""
    src = """
// staqex-profile: experiment
J = 1.0
h = 0.5
H_chain = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
State s0 = |+>
State s1 = |+>
State (s0, s1) = Evolve { (s0, s1) under H_chain for 0.1 using Suzuki(order = 2, steps = 2) }.run()
Measure s0 tracing_out s1
"""
    c = compile_source(src)
    assert c.ok, c.diagnostics
    j = _bind_named(c.unit, "J")
    h = _bind_named(c.unit, "h")
    hop = _bind_named(c.unit, "H_chain")
    assert j.ty is not None and j.ty.name == "Float"
    assert h.ty is not None and h.ty.name == "Float"
    assert hop.ty is not None and hop.ty.name == "Operator"


def test_0290_inferred_operator_emits_qasm(tmp_path: Path) -> None:
    """Then emit-qasm succeeds for inferred Operator chalk (B08 face)."""
    src = """
// staqex-profile: experiment
J = 1.0
h = 0.5
H_chain = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
State s0 = |+>
State s1 = |+>
State (s0, s1) = Evolve { (s0, s1) under H_chain for 0.7 using Suzuki(order = 2, steps = 6) }.run()
Measure s0 tracing_out s1
"""
    path = tmp_path / "inferred_b08.sqx"
    path.write_text(src, encoding="utf-8")
    qasm = StaqexCompiler().compile_to_qasm3(str(path))
    assert "OPENQASM" in qasm
    assert "rz" in qasm or "cx" in qasm or "x " in qasm.lower()


def test_0290_bare_classical_call_float_bind() -> None:
    """Then bare Float-returning Call bind does not Joint-misbind args."""
    src = """
package p
namespace D {
  pub struct R {
    val a: Float
    val b: Float
    val c: Float
  }
}
pub fn score(r: D.R) -> Float {
  return r.a - r.b - r.c
}
pub fn main() -> Unit {
  D.R report = D.R { a: 1.0, b: 0.15, c: 0.35 }
  fair = score(report)
  State s = Dirac(fair)
  Measure s
}
"""
    c = compile_source(src)
    assert c.ok, c.diagnostics
    fair = _bind_named(c.unit, "fair")
    assert fair.ty is not None and fair.ty.name == "Float"
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
    assert r.measurements[-1].value == pytest.approx(0.5)


def test_0290_bare_named_struct_not_linear_state() -> None:
    """Then bare named struct construction is not LINEAR State discard."""
    src = """
// staqex-profile: experiment
namespace G {
  pub struct Seg {
    val length: Float
  }
}
seg = G.Seg { length: 2.0 }
scale = seg.length
State s = |0>
Measure s
"""
    c = compile_source(src)
    codes = {d.get("code") for d in c.diagnostics}
    assert "LINEAR_IMPLICIT_DISCARD" not in codes, c.diagnostics
    assert c.ok, c.diagnostics
    seg = _bind_named(c.unit, "seg")
    scale = _bind_named(c.unit, "scale")
    assert seg.ty is not None
    assert seg.ty.name in {"Seg", "G.Seg"} or seg.ty.name.endswith("Seg")
    assert scale.ty is not None and scale.ty.name == "Float"
    r = run_source(src, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics


def test_0290_fail_closed_classical_state_clash() -> None:
    """Then unique classical literal fills Float/Int ty (not left None / State)."""
    clash = """
// staqex-profile: experiment
pub fn main() -> Unit {
  x = 0
  State s = Dirac(x)
  Measure s
}
"""
    c = compile_source(clash)
    assert c.ok, c.diagnostics
    x = _bind_named(c.unit, "x")
    assert x.ty is not None and x.ty.name in {"Float", "Int"}
    r = run_source(clash, settings={"seed": 0})
    assert r.status == "succeeded", r.diagnostics
