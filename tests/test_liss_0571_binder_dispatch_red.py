"""Phase 1 Red contracts for WP-0167 / LISS-0571 binder dispatch."""

from __future__ import annotations

import ast
from pathlib import Path

from compiler.staqex.host import run_source


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
BINDING = ROOT / "compiler/staqex/runtime/evaluation/binding.py"
COMPATIBILITY = ROOT / "compiler/staqex/runtime/evaluation/compatibility.py"
CONTEXT = ROOT / "compiler/staqex/runtime/evaluation/context.py"


def _evaluator_method_names() -> set[str]:
    tree = ast.parse(EVALUATOR.read_text(encoding="utf-8"))
    evaluator = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Evaluator"
    )
    return {
        node.name for node in evaluator.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_binding_successor_file_exists() -> None:
    assert BINDING.is_file()


def test_evaluator_binder_dispatch_bodies_leave_the_facade() -> None:
    remaining = _evaluator_method_names() & {"_bind", "_bind_names"}
    assert not remaining, sorted(remaining)


def test_binding_compatibility_wiring_is_declared() -> None:
    source = COMPATIBILITY.read_text(encoding="utf-8")
    for name in ("install_binding_compatibility", "bind_names", "bind"):
        assert name in source


def test_binding_context_declares_narrow_dispatch_callbacks() -> None:
    source = CONTEXT.read_text(encoding="utf-8")
    for callback in ("_bind_names", "_bind"):
        assert f"def {callback}" in source


def test_binding_successor_has_no_public_facade_dependency() -> None:
    assert BINDING.is_file()
    source = BINDING.read_text(encoding="utf-8")
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source


def test_simple_binder_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State<Int> observed = Dirac(1)
  Measure observed
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_classical_multi_bind_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  Int total = Sigma (i In 0..2) { i }
  State observed = Dirac(total)
  Measure observed
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_coin_binder_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State observed = Coin()
  Measure observed
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics
