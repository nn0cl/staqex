"""AT-TDD Phase 1 Red: semantic observation type boundary (ADR 0189)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import StateBind  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_non_destructive_inspection_has_a_diagnostic_view_type() -> None:
    """The view is typed distinctly while remaining terminally measurable."""

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            State viewed = inspect(psi)
            measure viewed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    assert compiled.unit is not None and compiled.unit.main is not None
    bind = next(
        stmt
        for stmt in compiled.unit.main.body.stmts
        if isinstance(stmt, StateBind) and stmt.names == ["viewed"]
    )
    assert compiled.checker.typed[id(bind.expr)].kind == "DiagnosticView"


if __name__ == "__main__":
    test_non_destructive_inspection_has_a_diagnostic_view_type()
    print("GREEN - semantic observation type boundary")
