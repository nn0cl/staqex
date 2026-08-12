"""Step 1.1 / AT-TDD: `enum` as exclusive physical classifications.

Physicist framing: mutually exclusive geometry / basis labels
(e.g. boundary conditions Periodic vs Open), not C-style ints.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import EnumDecl  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.evaluator import EnumValue  # noqa: E402


def test_enum_define_and_dot_ref() -> None:
    src = """
package t
enum BoundaryCondition {
    Periodic,
    Open
}
pub fn main() -> Unit {
    BoundaryCondition bc = BoundaryCondition.Open
    State x = dirac(0)
    measure x
}
"""
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    enums = [d for d in compiled.unit.decls if isinstance(d, EnumDecl)]
    assert len(enums) == 1
    assert enums[0].name == "BoundaryCondition"
    assert enums[0].variants == ["Periodic", "Open"]

    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics


def test_enum_rejects_int_literal() -> None:
    src = """
package t
enum BoundaryCondition { Periodic, Open }
pub fn main() -> Unit {
    BoundaryCondition bc = 1
    State x = dirac(0)
    measure x
}
"""
    codes = [d.get("code") for d in compile_source(src).diagnostics]
    assert "ENUM_TYPE_MISMATCH" in codes, codes


def test_enum_rejects_string_literal() -> None:
    src = """
package t
enum Basis { Z, X }
pub fn main() -> Unit {
    Basis b = "Z"
    State x = dirac(0)
    measure x
}
"""
    codes = [d.get("code") for d in compile_source(src).diagnostics]
    assert "ENUM_TYPE_MISMATCH" in codes, codes


def test_enum_runtime_tag() -> None:
    src = """
package t
namespace Geometry {
  enum BoundaryCondition { Periodic, Open }
}
pub fn main() -> Unit {
  Geometry.BoundaryCondition bc = Geometry.BoundaryCondition.Periodic
  State x = dirac(0)
  measure x
}
"""
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics
    # Construct via evaluator path used by Type-First enum binds
    from compiler.staqex.runtime.evaluator import Evaluator

    ev = Evaluator(seed=0)
    assert compiled.unit is not None
    # Register enums as run_unit would
    for d in compiled.unit.decls:
        if isinstance(d, EnumDecl):
            ev.enums[d.qualified_name] = d
            ev.enums[d.name] = d
    from compiler.staqex.ast_nodes import Attr, Var, Span

    sp = Span(1, 1)
    val = ev._eval_value(
        Attr(
            obj=Attr(obj=Var(name="Geometry", span=sp), name="BoundaryCondition", span=sp),
            name="Periodic",
            span=sp,
        ),
        {},
    )
    assert isinstance(val, EnumValue)
    assert val.variant == "Periodic"


if __name__ == "__main__":
    test_enum_define_and_dot_ref()
    test_enum_rejects_int_literal()
    test_enum_rejects_string_literal()
    test_enum_runtime_tag()
    print("OK — enum support (Step 1.1)")
