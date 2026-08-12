"""AT-TDD Phase 1 Red: LISS-0329 -- reject duplicate predicate names in
`feasible(...)`.

Target: `compiler/staqex/pipeline.py::_collect_feasible_predicates`. A
repeated predicate name (e.g. `exactly_selected` given twice, with
different values) currently compiles clean and silently resolves to the
last value at runtime -- a source-level contradiction should fail closed
at compile time instead.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(diagnostics: list[dict[str, object]]) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


_SOURCE_DUPLICATE_PREDICATE = """
package s02
pub fn main() -> Unit {
  State selection = prepare_selection(3)
  State feasible = project selection onto feasible(
    exactly_selected = 2,
    exactly_selected = 3,
  )
  Measure feasible
}
"""

_SOURCE_DISTINCT_PREDICATES = """
package s02
pub fn main() -> Unit {
  State selection = prepare_selection(3)
  State feasible = project selection onto feasible(
    exactly_selected = 2,
    pairwise_compatible = true,
  )
  Measure feasible
}
"""


def test_repeated_predicate_name_fails_closed() -> None:
    compiled = compile_source(_SOURCE_DUPLICATE_PREDICATE)

    codes = _codes(compiled.diagnostics)
    assert "S02_DUPLICATE_CONSTRAINT_PREDICATE" in codes
    assert not compiled.ok


def test_distinct_predicate_names_are_unaffected() -> None:
    compiled = compile_source(_SOURCE_DISTINCT_PREDICATES)

    codes = _codes(compiled.diagnostics)
    assert "S02_DUPLICATE_CONSTRAINT_PREDICATE" not in codes
    assert compiled.ok, compiled.diagnostics
