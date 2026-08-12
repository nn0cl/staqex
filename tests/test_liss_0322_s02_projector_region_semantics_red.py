"""AT-TDD Phase 1 Red: LISS-0322 Projector<Selection> region semantics.

Target behavior is docs/specs/staqex-v1-s02-drug-discovery-benchmark.md's
"Acceptance scenarios -- Projector<Selection> semantics (ADR 0192, Phase 1
target, LISS-0322)". Kernel-side IR lowering only
(compiler/staqex/pipeline.py::_append_selection_projector_region); no
grammar/parser change.

These tests intentionally describe the not-yet-implemented behavior. They
must fail against the current compiler, which unconditionally appends one
ProjectorRegion with the hardcoded literal constraint_ref="S02.feasible"
whenever any `project(...)` call exists anywhere in `main`'s body --
regardless of what the projection target actually says.
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


def _projector_regions(compiled) -> list[object]:
    if compiled.quantum_semantic_ir is None:
        return []
    return [
        region
        for region in compiled.quantum_semantic_ir.regions
        if type(region).__name__ == "ProjectorRegion"
    ]


_SOURCE_EXACTLY_SELECTED = """
package s02
pub fn main() -> Unit {
  State candidates = finiteize(0.0, 1.0, 8, 16, 0)
  State selection = prepare_selection(candidates)
  State feasible = project selection onto feasible(
    exactly_selected = 2,
    pairwise_compatible = true,
  )
  Measure feasible
}
"""

_SOURCE_DIVERSITY = """
package s02
pub fn main() -> Unit {
  State candidates = finiteize(0.0, 1.0, 8, 16, 0)
  State selection = prepare_selection(candidates)
  State feasible = project selection onto feasible(
    diversity_at_least = 3,
  )
  Measure feasible
}
"""

_SOURCE_UNKNOWN_PREDICATE = """
package s02
pub fn main() -> Unit {
  State candidates = finiteize(0.0, 1.0, 8, 16, 0)
  State selection = prepare_selection(candidates)
  State feasible = project selection onto feasible(
    unknown_rule = 1,
  )
  Measure feasible
}
"""

_SOURCE_NO_PROJECTOR = """
package s02
pub fn main() -> Unit {
  State candidates = finiteize(0.0, 1.0, 8, 16, 0)
  State selection = prepare_selection(candidates)
  Measure selection
}
"""


def test_recognized_predicates_produce_source_derived_constraint_ref() -> None:
    compiled = compile_source(_SOURCE_EXACTLY_SELECTED)

    assert compiled.ok, compiled.diagnostics
    regions = _projector_regions(compiled)
    assert len(regions) == 1
    ref = regions[0].constraint_ref
    assert ref != "S02.feasible"
    assert "exactly_selected" in ref
    assert "pairwise_compatible" in ref


def test_different_predicate_set_produces_different_constraint_ref() -> None:
    exactly_selected_ref = _projector_regions(
        compile_source(_SOURCE_EXACTLY_SELECTED)
    )[0].constraint_ref
    diversity_ref = _projector_regions(compile_source(_SOURCE_DIVERSITY))[0]
    diversity_ref = diversity_ref.constraint_ref

    assert diversity_ref != exactly_selected_ref
    assert "diversity_at_least" in diversity_ref


def test_unrecognized_predicate_fails_closed() -> None:
    compiled = compile_source(_SOURCE_UNKNOWN_PREDICATE)

    codes = _codes(compiled.diagnostics)
    assert "S02_UNKNOWN_CONSTRAINT_PREDICATE" in codes
    assert not compiled.ok
    assert not _projector_regions(compiled)


def test_penalty_only_program_produces_no_projector_region() -> None:
    compiled = compile_source(_SOURCE_NO_PROJECTOR)

    assert compiled.ok, compiled.diagnostics
    assert not _projector_regions(compiled)


if __name__ == "__main__":
    test_recognized_predicates_produce_source_derived_constraint_ref()
    test_different_predicate_set_produces_different_constraint_ref()
    test_unrecognized_predicate_fails_closed()
    test_penalty_only_program_produces_no_projector_region()
    print("GREEN — Projector<Selection> region semantics")
