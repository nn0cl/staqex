"""Modern OOP + visibility (ADR 0058 revised): pub / module / underscore."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.access import can_access  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_path, run_source  # noqa: E402


def test_can_access_modern_matrix() -> None:
    assert can_access(
        visibility="private",
        decl_package=["a"],
        use_package=["a"],
        same_class=True,
    )
    assert not can_access(
        visibility="private",
        decl_package=["a"],
        use_package=["a"],
        same_class=False,
    )
    assert can_access(
        visibility="module",
        decl_package=["a", "b"],
        use_package=["a", "c"],
        same_module=True,
    )
    assert not can_access(
        visibility="module",
        decl_package=["a"],
        use_package=["z"],
        same_module=False,
    )
    assert can_access(
        visibility="public",
        decl_package=["a"],
        use_package=["z"],
        same_module=False,
    )
    # legacy package alias → module
    assert can_access(
        visibility="package",
        decl_package=["a"],
        use_package=["b"],
        same_module=True,
    )


def test_underscore_private_field_rejected() -> None:
    src = """
package t
class SSHSystem {
  var _t: Float = 0.0
  pub val params: Float = 1.0

  pub fn step() -> Float {
    this._t = this._t + 1.0
    return this._t
  }
}
pub fn main() -> Unit {
  SSHSystem s = SSHSystem()
  Float leaked = s._t
  measure leaked
}
"""
    compiled = compile_source(src)
    codes = [d.get("code") for d in compiled.diagnostics]
    assert "PRIVATE_ACCESS_VIOLATION_ERROR" in codes, compiled.diagnostics
    assert not compiled.ok


def test_underscore_ok_inside_class() -> None:
    src = """
package t
class SSHSystem {
  var _t: Float = 0.0

  pub fn step() -> Float {
    this._t = this._t + 1.0
    Float done = 1.0
    return done
  }
}
pub fn main() -> Unit {
  SSHSystem s = SSHSystem()
  Float x = s.step()
  measure x
}
"""
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics


def test_pub_alias_and_enum_struct_class() -> None:
    src = """
package t
namespace Topology.SSH {
  pub enum BoundaryCondition { Periodic, Open }
  pub struct SSHParams {
    pub val v_intra: Float
    pub val w_inter: Float
  }
  pub class SSHSystem {
    var _t: Float = 0.0
    pub val params: Topology.SSH.SSHParams
    pub val bc: Topology.SSH.BoundaryCondition

    fn init(p: Topology.SSH.SSHParams, boundary: Topology.SSH.BoundaryCondition) {
      this.params = p
      this.bc = boundary
    }

    pub fn step() -> Float {
      this._t = this._t + 0.1
      Float done = 1.0
      return done
    }
  }
}
pub fn main() -> Unit {
  Topology.SSH.BoundaryCondition bc = Topology.SSH.BoundaryCondition.Open
  Topology.SSH.SSHParams p = Topology.SSH.SSHParams(0.5, 1.5)
  Topology.SSH.SSHSystem sys = Topology.SSH.SSHSystem(p, Topology.SSH.BoundaryCondition.Open)
  Float ok = sys.step()
  measure ok
}
"""
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics


def test_fun_init_constructor() -> None:
    src = """
package t
struct P { val v: Float }
class Box {
  val params: P
  fn init(p: P) {
    this.params = p
  }
  pub fn read() -> Float {
    Float y = this.params.v
    return y
  }
}
pub fn main() -> Unit {
  P p = P(2.5)
  Box b = Box(p)
  Float v = b.read()
  measure v
}
"""
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 2.5


def test_module_private_cross_module() -> None:
    """Non-`pub` symbol referenced across named modules → MODULE_PRIVATE_ACCESS_ERROR."""
    import tempfile

    from compiler.staqex.pipeline import compile_path

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        lib = root / "lib"
        app = root / "app"
        lib.mkdir()
        app.mkdir()
        (lib / "module-info.sqx").write_text(
            "module demo.lib {\n}\n", encoding="utf-8"
        )
        (app / "module-info.sqx").write_text(
            "module demo.app {\n}\n", encoding="utf-8"
        )
        (lib / "secret.sqx").write_text(
            """
package demo.lib
fn hidden() -> Float {
  Float x = 1.0
  return x
}
""",
            encoding="utf-8",
        )
        entry = app / "main.sqx"
        entry.write_text(
            """
package demo.app
import demo.lib.secret
pub fn main() -> Unit {
  Float y = hidden()
  measure y
}
""",
            encoding="utf-8",
        )
        # Import resolution is entry_dir-relative; place a reachable copy via rglob
        # by putting lib under app parent and importing with path that rglob finds.
        # resolve_import_path uses entry_dir=app, so copy/link secret into search path:
        # use package path demo.lib.secret with entry package demo.app → rel lib/secret
        (app / "lib").mkdir()
        (app / "lib" / "secret.sqx").write_text(
            (lib / "secret.sqx").read_text(encoding="utf-8"), encoding="utf-8"
        )
        (app / "lib" / "module-info.sqx").write_text(
            "module demo.lib {\n}\n", encoding="utf-8"
        )
        compiled = compile_path(entry)
        codes = [d.get("code") for d in compiled.diagnostics]
        assert "MODULE_PRIVATE_ACCESS_ERROR" in codes, compiled.diagnostics
        assert not compiled.ok


def test_protected_forbidden() -> None:
    src = """
package t
protected class Bad {
}
pub fn main() -> Unit {
  State x = dirac(0)
  measure x
}
"""
    compiled = compile_source(src)
    codes = [d.get("code") for d in compiled.diagnostics]
    assert any(
        c in {"FORBIDDEN", "FORBIDDEN_CONSTRUCT", "PARSE_ERROR", "LEX_ERROR"}
        or (isinstance(c, str) and "FORBIDDEN" in c)
        for c in codes
    ) or any("protected" in str(d.get("message", "")).lower() for d in compiled.diagnostics), (
        compiled.diagnostics
    )


def test_example10_no_module_info_required() -> None:
    entry = _REPO / "examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx"
    result = run_path(entry, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None


if __name__ == "__main__":
    test_can_access_modern_matrix()
    test_underscore_private_field_rejected()
    test_underscore_ok_inside_class()
    test_pub_alias_and_enum_struct_class()
    test_fun_init_constructor()
    test_module_private_cross_module()
    test_protected_forbidden()
    test_example10_no_module_info_required()
    print("OK — modern OOP + visibility")
