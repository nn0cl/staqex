"""AT-TDD Phase 1 Red: LISS-0320 `superpose` formal grammar and type boundary.

Target behavior is docs/specs/staqex-v1-quantum-mental-model-follow-up.md
§4.5. `superpose` must become a real, first-class construct in the ordinary
language surface (a distinct ``SuperposeExpr`` AST node), never silently
accepted as ``mix``/``WhenExpr``, and must fail closed with one explicit
diagnostic if a program tries to evaluate it (real coherent execution is a
separate, later slice).

These tests intentionally describe the not-yet-implemented surface. They
must fail against the current compiler, which only recognizes ``superpose``
inside the shallow ``H1Superposition`` line-lexeme heuristic (PR #344), not
in the ordinary grammar. `superpose (...) { ... }` on the ordinary surface
currently fails to parse.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import StateBind, WhenExpr  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402


def _codes(diagnostics: list[dict[str, object]]) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


_SUPERPOSE_SOURCE = """
package liss0320
pub fn main() -> Unit {
  State control = coin()
  State result = superpose (control) {
    0 -> |0>,
    1 -> |1>,
  }
  measure result
}
"""

_MIX_SOURCE = """
package liss0320
pub fn main() -> Unit {
  State control = coin()
  State result = mix (control) {
    0 -> |0>,
    1 -> |1>,
  }
  measure result
}
"""

_WHEN_SOURCE = """
package liss0320
pub fn main() -> Unit {
  State control = coin()
  State result = when (control) {
    0 -> |0>,
    1 -> |1>,
  }
  measure result
}
"""


def _result_bind_expr(unit) -> object:
    return next(
        stmt.expr
        for stmt in unit.main.body.stmts
        if isinstance(stmt, StateBind) and stmt.names == ["result"]
    )


def test_superpose_parses_to_distinct_ast_node() -> None:
    """`superpose (control) { ... }` must parse to a `SuperposeExpr`, not a
    `PARSE_ERROR` and not a `WhenExpr`."""

    compiled = compile_source(_SUPERPOSE_SOURCE)

    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None and compiled.unit.main is not None

    from compiler.staqex.ast_nodes import SuperposeExpr  # target node (LISS-0320)

    expr = _result_bind_expr(compiled.unit)
    assert isinstance(expr, SuperposeExpr)
    assert not isinstance(expr, WhenExpr)


def test_superpose_type_checks_as_state_and_is_not_a_mixture() -> None:
    """Type-checking `superpose` must succeed and must not classify it as a
    `mix`/`Mixture` composition."""

    compiled = compile_source(_SUPERPOSE_SOURCE)

    assert compiled.ok, compiled.diagnostics
    codes = _codes(compiled.diagnostics)
    assert "RETIRED_KEYWORD" not in codes
    assert not any(
        "mixture" in str(d.get("message", "")).lower() for d in compiled.diagnostics
    )


def test_mix_and_when_ordinary_surface_are_unaffected() -> None:
    """Regression guard: existing `mix`/`when` ordinary-surface behavior must
    stay exactly as shipped while `superpose` grammar is added."""

    mix_compiled = compile_source(_MIX_SOURCE)
    assert mix_compiled.ok, mix_compiled.diagnostics
    assert isinstance(_result_bind_expr(mix_compiled.unit), WhenExpr)

    when_codes = _codes(compile_source(_WHEN_SOURCE).diagnostics)
    assert "RETIRED_KEYWORD" in when_codes


def test_evaluating_superpose_fails_closed_not_open() -> None:
    """Attempting to actually run a `superpose` program must not crash with
    an unhandled-node exception and must not silently execute `mix`
    semantics. It must fail with one explicit, documented diagnostic."""

    result = run_source(_SUPERPOSE_SOURCE, settings={"target": "local", "seed": 0})

    codes = _codes(list(result.diagnostics))
    assert result.status == "failed"
    assert "COHERENT_EXECUTION_UNSUPPORTED" in codes
    assert not result.measurements


if __name__ == "__main__":
    test_superpose_parses_to_distinct_ast_node()
    test_superpose_type_checks_as_state_and_is_not_a_mixture()
    test_mix_and_when_ordinary_surface_are_unaffected()
    test_evaluating_superpose_fails_closed_not_open()
    print("GREEN — superpose formal grammar and type boundary")
