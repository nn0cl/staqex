"""Regression coverage for the completed LISS-0491 evaluator migration."""

from __future__ import annotations

import io
from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex import host, run  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


SOURCE = """
package liss0491
pub fn main() -> Unit {
    State a = Coin()
    Measure a
}
"""


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return compiled


def test_host_delivery_passes_compile_owned_semantics_to_canonical_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    original = Evaluator.run_canonical_unit

    def spy(self, unit, *, semantic_ir=None, stdout=None):
        calls.append(semantic_ir)
        return original(self, unit, semantic_ir=semantic_ir, stdout=stdout)

    monkeypatch.setattr(Evaluator, "run_canonical_unit", spy)
    result = host.run_source(SOURCE, settings={"target": "local"}, stdout=io.StringIO())

    assert result.status == "succeeded"
    assert len(calls) == 1
    assert calls[0] is not None


def test_run_module_delivery_passes_compile_owned_semantics_to_canonical_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    original = Evaluator.run_canonical_unit

    def spy(self, unit, *, semantic_ir=None, stdout=None):
        calls.append(semantic_ir)
        return original(self, unit, semantic_ir=semantic_ir, stdout=stdout)

    monkeypatch.setattr(Evaluator, "run_canonical_unit", spy)
    result = run.run_source(SOURCE, seed=0, stdout=io.StringIO())

    assert result.compile_ok
    assert len(calls) == 1
    assert calls[0] is not None


def test_legacy_entry_is_removed_after_complete_migration() -> None:
    assert not hasattr(Evaluator, "run_unit")


def test_production_code_has_no_unclassified_direct_legacy_callers() -> None:
    offenders: list[str] = []
    for path in (REPO / "compiler" / "staqex").rglob("*.py"):
        if path.name == "evaluator.py":
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if ".run_unit(" in line:
                offenders.append(f"{path.relative_to(REPO)}:{line_no}")

    assert offenders == [], "migrate or explicitly classify legacy callers: " + ", ".join(offenders)


def test_canonical_execution_preserves_terminal_measurement_and_provenance() -> None:
    compiled = _compiled()
    result = Evaluator(seed=0).run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=io.StringIO(),
    )

    assert result.execution_authority == "scientific_semantic_ir"
    assert result.measure is not None
    assert result.measurement_kind is not None
    assert result.source_id == compiled.scientific_semantic_ir.source_id
