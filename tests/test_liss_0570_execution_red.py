"""Phase 1 Red contracts for WP-0167 / LISS-0570 Unit A1."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from compiler.staqex.host import run_source


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
EXECUTION = ROOT / "compiler/staqex/runtime/evaluation/execution.py"
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


def test_execution_successor_file_exists() -> None:
    assert EXECUTION.is_file()


def test_evaluator_execution_bodies_leave_the_facade() -> None:
    remaining = _evaluator_method_names() & {
        "_run_legacy_ast_body",
        "_run_unit_body",
    }
    assert not remaining, sorted(remaining)


def test_execution_compatibility_wiring_is_declared() -> None:
    source = COMPATIBILITY.read_text(encoding="utf-8")
    assert "install_execution_compatibility" in source
    assert "execute_legacy_ast_body" in source
    assert "run_unit_body" in source


def test_execution_context_declares_narrow_run_callbacks() -> None:
    source = CONTEXT.read_text(encoding="utf-8")
    for callback in ("_prepare_execution_state", "_execute_main_statement"):
        assert f"def {callback}" in source


def test_execution_successor_has_no_public_facade_dependency() -> None:
    assert EXECUTION.is_file()
    source = EXECUTION.read_text(encoding="utf-8")
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source


def test_simple_execution_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State<Int> value = Dirac(1 + 2)
  Measure value
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_classical_and_quantum_statement_routing_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  Int total = 2 + 3
  State<Int> value = Dirac(total)
  Measure value
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_execution_diagnostics_characterization_remains_fail_closed() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State<Int> value = vacuum()
  Measure value
}
""",
        settings={"seed": 0},
    )
    assert result.status != "succeeded"
    assert result.diagnostics
