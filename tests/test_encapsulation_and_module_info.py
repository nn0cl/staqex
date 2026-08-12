"""AT-TDD: ADR 0058 revised — pub / module / `_` (module-info optional)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.access import can_access  # noqa: E402
from compiler.staqex.pipeline import compile_path, compile_source  # noqa: E402
from compiler.staqex.run import run_path  # noqa: E402
from compiler.staqex.typecheck import TypeChecker  # noqa: E402


def test_can_access_matrix() -> None:
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


def test_private_method_access_violation() -> None:
    tc = TypeChecker()
    tc.check_access_bounds(
        visibility="private",
        name="secret",
        decl_package=["demo"],
        use_package=["demo"],
        span_line=1,
        span_col=1,
        same_class=False,
    )
    assert any(
        d.get("code")
        in {"ACCESS_CONTROL_VIOLATION_ERROR", "PRIVATE_ACCESS_VIOLATION_ERROR"}
        for d in tc.diagnostics
    )


def test_module_info_exports_not_required() -> None:
    """Named module-info may exist, but missing exports must not hard-fail."""
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "module-info.sqx").write_text(
            """
module demo.app {
  exports visible;
}
""",
            encoding="utf-8",
        )
        (root / "hidden").mkdir()
        (root / "hidden" / "secret.sqx").write_text(
            """
package demo.app.hidden
pub fn leak() -> Float {
  Float x = 1.0
  return x
}
""",
            encoding="utf-8",
        )
        entry = root / "main.sqx"
        entry.write_text(
            """
package demo.app
import demo.app.hidden.secret
pub fn main() -> Unit {
  State observed = dirac(0)
  measure observed
}
""",
            encoding="utf-8",
        )
        compiled = compile_path(entry)
        codes = [d.get("code") for d in compiled.diagnostics]
        assert "PACKAGE_NOT_EXPORTED_ERROR" not in codes, codes
        assert compiled.ok, compiled.diagnostics


def test_example10_runs() -> None:
    entry = _REPO / "examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx"
    compiled = compile_path(entry)
    hard = [
        d
        for d in compiled.diagnostics
        if d.get("code")
        in {
            "PARSE_ERROR",
            "PRIVATE_ACCESS_VIOLATION_ERROR",
            "MODULE_PRIVATE_ACCESS_ERROR",
            "MODULE_NOT_FOUND_ERROR",
        }
    ]
    assert not hard, hard
    result = run_path(entry, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None


def test_pub_keyword_parses() -> None:
    src = """
package t
pub enum BoundaryCondition { Periodic, Open }
pub fn main() -> Unit {
  BoundaryCondition bc = BoundaryCondition.Open
  State x = dirac(0)
  measure x
}
"""
    assert compile_source(src).ok


if __name__ == "__main__":
    test_can_access_matrix()
    test_private_method_access_violation()
    test_module_info_exports_not_required()
    test_example10_runs()
    test_pub_keyword_parses()
    print("OK — encapsulation (modern)")
