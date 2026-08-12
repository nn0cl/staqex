"""AT-TDD: namespace / enum / struct / class (ADR 0055–0056 OOP surface)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import EnumDecl, StructDecl  # noqa: E402
from compiler.staqex.pipeline import compile_path, compile_source  # noqa: E402
from compiler.staqex.run import run_path, run_source  # noqa: E402


def test_enum_variant_and_reject_int() -> None:
    ok = """
package t
enum BoundaryCondition { Periodic, Open }
pub fn main() -> Unit {
  BoundaryCondition bc = BoundaryCondition.Open
  State x = dirac(0)
  measure x
}
"""
    bad = """
package t
enum BoundaryCondition { Periodic, Open }
pub fn main() -> Unit {
  BoundaryCondition bc = 1
  State x = dirac(0)
  measure x
}
"""
    c_ok = compile_source(ok)
    assert c_ok.ok, c_ok.diagnostics
    enums = [d for d in c_ok.unit.decls if isinstance(d, EnumDecl)]
    assert enums and "Open" in enums[0].variants

    c_bad = compile_source(bad)
    codes = [d.get("code") for d in c_bad.diagnostics]
    assert "ENUM_TYPE_MISMATCH" in codes, codes


def test_struct_immutable_and_copy() -> None:
    src = """
package t
struct P { val a: Float, val b: Float }
class Box {
  var n: Float = 0.0
  pub fn take(p) -> Float {
    this.n = p.a
    Float out = this.n
    return out
  }
}
pub fn main() -> Unit {
  P p = P(1.0, 2.0)
  Box b = Box()
  Float x = b.take(p)
  measure x
}
"""
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics
    assert r.eval.measure is not None
    assert r.eval.measure.value == 1.0

    imm = """
package t
struct P { val a: Float }
pub fn main() -> Unit {
  P p = P(1.0)
  p.a = 2.0
  measure p.a
}
"""
    # assignment to struct field — parse + runtime/type error
    c = compile_source(imm)
    # may PARSE as AssignStmt then IMMUTABLE at typecheck
    codes = [d.get("code") for d in c.diagnostics]
    assert "IMMUTABLE_ASSIGNMENT_ERROR" in codes or not c.ok


def test_class_this_var_mutation() -> None:
    src = """
package t
namespace N {
  class Counter {
    var ticks: Float = 0.0
    pub fn bump() -> Float {
      this.ticks = this.ticks + 1.0
      Float out = this.ticks
      return out
    }
  }
}
pub fn main() -> Unit {
  N.Counter c = N.Counter()
  Float a = c.bump()
  Float b = c.bump()
  measure b
}
"""
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics
    assert r.eval.measure.value == 2.0


def test_namespace_dot_resolution() -> None:
    src = """
package t
namespace A.B {
  enum E { X, Y }
  struct S { val n: Int }
}
pub fn main() -> Unit {
  A.B.E e = A.B.E.Y
  A.B.S s = A.B.S(7)
  State x = dirac(0)
  measure x
}
"""
    c = compile_source(src)
    assert c.ok, c.diagnostics
    structs = [d.qualified_name for d in c.unit.decls if isinstance(d, StructDecl)]
    assert "A.B.S" in structs
    r = run_source(src, seed=0, stdout=io.StringIO())
    assert r.compile_ok, r.diagnostics


def test_example10_ssh_linked_run() -> None:
    entry = _REPO / "examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx"
    assert entry.is_file()
    compiled = compile_path(entry)
    hard = [
        d
        for d in compiled.diagnostics
        if d.get("code")
        in {
            "PARSE_ERROR",
            "LEX_ERROR",
            "MODULE_NOT_FOUND_ERROR",
            "ENUM_TYPE_MISMATCH",
            "IMMUTABLE_ASSIGNMENT_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
        }
    ]
    assert not hard, hard
    result = run_path(entry, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None


if __name__ == "__main__":
    test_enum_variant_and_reject_int()
    test_struct_immutable_and_copy()
    test_class_this_var_mutation()
    test_namespace_dot_resolution()
    test_example10_ssh_linked_run()
    print("OK — OOP namespace/enum/struct/class")
