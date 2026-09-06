"""AT-TDD Phase 1 Red: lexical scope and State shadowing (ADR 0216)."""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source
from compiler.staqex.scientific_lexicon_contract import inspect_source


def test_inner_state_shadow_is_a_distinct_binding_and_outer_restores():
    source = """package scoped
pub fn main() -> Unit {
    State psi = |0>
    State result = {
        let psi = |+>
        psi
    }
    Measure result
}
"""
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = inspect_source(source, source_id="inner-state.sqx")

    bindings = result.scoped_bindings
    assert [binding.name for binding in bindings] == ["psi", "psi"]
    assert [binding.scope_depth for binding in bindings] == [0, 1]
    assert bindings[0].binding_id != bindings[1].binding_id
    assert bindings[0].declaration_span != bindings[1].declaration_span


def test_inner_classical_shadow_does_not_change_outer_state_binding():
    source = """package scoped
pub fn main() -> Unit {
    State psi = |0>
    Float value = {
        let psi = 0.5
        psi
    }
    Measure psi
}
"""
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = inspect_source(source, source_id="inner-classical.sqx")

    bindings = result.scoped_bindings
    assert [(binding.name, binding.context) for binding in bindings] == [
        ("psi", "quantum_state"),
        ("psi", "classical_scalar"),
    ]


def test_same_scope_duplicate_declaration_is_rejected():
    source = """package scoped
pub fn main() -> Unit {
    State psi = |0>
    State psi = |+>
    Measure psi
}
"""
    codes = {str(diagnostic.get("code")) for diagnostic in compile_source(source).diagnostics}
    assert "DUPLICATE_DECLARATION" in codes


def test_state_consumption_is_tracked_per_shadow_binding():
    source = """package scoped
pub fn main() -> Unit {
    State psi = |0>
    State result = {
        let psi = |+>
        |0>
    }
    Measure psi
}
"""
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    codes = {str(diagnostic.get("code")) for diagnostic in compiled.diagnostics}
    assert "LINEAR_DUPLICATE_USE" not in codes
    result = inspect_source(source, source_id="per-binding.sqx")
    assert len(result.scoped_bindings) == 2
