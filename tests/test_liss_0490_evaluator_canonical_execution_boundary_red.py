"""AT-TDD Phase 1 Red: LISS-0490 evaluator canonical execution boundary."""

from __future__ import annotations

from dataclasses import replace
import io
from pathlib import Path
import sys

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator, KernelDiagnosticError


SOURCE = (REPO / "tests/fixtures/semantic_core/evaluator_boundary.sqx").read_text(
    encoding="utf-8"
)


def _compiled():
    compiled = compile_source(SOURCE)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    assert compiled.scientific_semantic_ir is not None
    return compiled


def _run(compiled, **kwargs):
    return Evaluator(seed=7).run_canonical_unit(
        compiled.unit, stdout=io.StringIO(), **kwargs
    )


def test_local_execution_accepts_compile_owned_semantic_ir() -> None:
    compiled = _compiled()
    result = _run(compiled, semantic_ir=compiled.scientific_semantic_ir)
    assert result.execution_authority == "scientific_semantic_ir"


def test_execution_without_canonical_semantics_rejects_before_mutation() -> None:
    compiled = _compiled()
    with pytest.raises(KernelDiagnosticError):
        Evaluator(seed=7).run_canonical_unit(compiled.unit)


def test_mismatched_canonical_source_rejects_without_measurement() -> None:
    compiled = _compiled()
    mismatched = replace(compiled.scientific_semantic_ir, source_id="other.sqx")
    with pytest.raises(KernelDiagnosticError):
        _run(compiled, semantic_ir=mismatched)


def test_terminal_measurement_is_the_only_collapse_boundary() -> None:
    compiled = _compiled()
    result = _run(compiled, semantic_ir=compiled.scientific_semantic_ir)
    assert result.measure is not None
    assert result.measure.output
    assert result.measurement_kind is not None


def test_nonterminal_state_execution_does_not_emit_measurement() -> None:
    compiled = _compiled()
    result = _run(compiled, semantic_ir=compiled.scientific_semantic_ir)
    assert result.measure is None or result.measurement_kind != "intermediate"


def test_exact_symbolic_execution_has_no_finite_allocation() -> None:
    compiled = _compiled()
    result = _run(compiled, semantic_ir=compiled.scientific_semantic_ir)
    assert not hasattr(result, "finite_plan")
    assert not hasattr(result, "allocation")


def test_ports_are_the_only_entropy_and_measurement_effect_boundary() -> None:
    compiled = _compiled()
    result = _run(compiled, semantic_ir=compiled.scientific_semantic_ir)
    assert result.rng_calls_before_measure >= 0
    assert result.measure is not None


def test_repeated_canonical_execution_preserves_authority_and_provenance() -> None:
    compiled = _compiled()
    first = _run(compiled, semantic_ir=compiled.scientific_semantic_ir)
    second = _run(compiled, semantic_ir=compiled.scientific_semantic_ir)
    assert first.execution_authority == second.execution_authority == "scientific_semantic_ir"
    assert first.measure is not None and second.measure is not None
