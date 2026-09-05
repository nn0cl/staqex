"""AT-TDD Phase 1 Red: LISS-0480 scientific lexicon contract."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _inspect(source: str, *, source_id: str):
    from compiler.staqex.scientific_lexicon_contract import inspect_source

    return inspect_source(source, source_id=source_id)


def test_lexicon_fixture_inventory_is_reachable() -> None:
    source_id = "tests/fixtures/scientific_lexicon/aliases_and_contexts.sqx"
    source_path = REPO / source_id

    assert source_path.is_file()
    result = _inspect(source_path.read_text(encoding="utf-8"), source_id=source_id)

    assert result.source_id == source_id
    assert result.contract_version == "scientific-lexicon-v1"


def test_ascii_alias_and_blackboard_display_form_share_one_identity() -> None:
    source_id = "tests/fixtures/scientific_lexicon/aliases_and_contexts.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")
    result = _inspect(source, source_id=source_id)

    psi = result.bindings["psi"]
    assert psi.canonical_id == "psi"
    assert psi.display_symbol == "ψ"
    assert psi.token_class == "scientific_identifier"
    assert psi.context == "quantum_state"
    assert psi.written_form == "psi"
    assert psi.semantic_operation is None


def test_alias_provenance_is_preserved_without_creating_a_second_dialect() -> None:
    source_id = "tests/fixtures/scientific_lexicon/aliases_and_contexts.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")
    result = _inspect(source, source_id=source_id)

    commutator = result.operations[0]
    assert commutator.canonical_id == "commutator"
    assert commutator.written_form == "cm"
    assert commutator.display_form == "[X, Y]"
    assert commutator.token_class == "scientific_operator_alias"
    assert commutator.semantic_operation == "commutator"


def test_contextual_classical_name_remains_available_and_shadowing_is_deterministic() -> None:
    source_id = "tests/fixtures/scientific_lexicon/shadowing.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")
    result = _inspect(source, source_id=source_id)

    assert result.bindings["x"].token_class == "ordinary_identifier"
    assert result.bindings["x"].context == "classical_scalar"
    assert result.shadowing_policy == "nearest_typed_declaration"


def test_unsupported_scientific_spelling_has_actionable_diagnostic() -> None:
    with pytest.raises(ValueError, match="unsupported scientific spelling") as error:
        _inspect(
            "State ψ = |0>",
            source_id="synthetic.scientific_lexicon.unicode-source.sqx",
        )

    assert "use the canonical ASCII spelling" in str(error.value)
