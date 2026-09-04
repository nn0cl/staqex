"""AT-TDD Phase 1 Red: LISS-0492 complete ``run_unit`` removal contract."""

from __future__ import annotations

import io
from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


SOURCE = """
package liss0492
pub fn main() -> Unit {
    State a = Coin()
    Measure a
}
"""


def _canonical_run(source: str):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )


def test_canonical_test_helper_is_the_only_supported_execution_helper() -> None:
    result = _canonical_run(SOURCE)

    assert result.execution_authority == "scientific_semantic_ir"
    assert result.source_id == "<memory>"


def test_public_legacy_run_unit_api_is_absent_after_removal() -> None:
    assert not hasattr(Evaluator, "run_unit")


def test_no_executable_legacy_run_unit_references_remain() -> None:
    excluded = {
        Path("tests/test_liss_0491_evaluator_legacy_run_unit_retirement_red.py"),
        Path("tests/test_liss_0492_evaluator_run_unit_complete_removal_red.py"),
    }
    offenders: list[str] = []
    for root in (REPO / "compiler", REPO / "tests"):
        for path in root.rglob("*.py"):
            relative = path.relative_to(REPO)
            if relative in excluded:
                continue
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if ".run_unit(" in line:
                    offenders.append(f"{relative}:{line_no}")

    assert offenders == [], "remove executable legacy references: " + ", ".join(offenders)


def test_canonical_execution_keeps_terminal_measure_and_ports_unchanged() -> None:
    result = _canonical_run(SOURCE)

    assert result.measure is not None
    assert result.measurement_kind is not None
    assert result.rng_calls_before_measure >= 0
