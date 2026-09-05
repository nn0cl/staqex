"""AT-TDD Phase 1 Red: LISS-0481 observation contract.

The packet fixes the semantic boundary without adding public observation
types, general POVM support, tomography, or a numerical backend.  The
provider-neutral inspection API is intentionally absent until Phase 2 Green.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _inspect(source: str, *, source_id: str):
    from compiler.staqex.observation_contract import inspect_source

    return inspect_source(source, source_id=source_id)


def test_source_fixture_is_reachable_and_preserves_inspect_then_measure_order() -> None:
    source_id = "tests/fixtures/observation_contract/inspect_then_measure.sqx"
    source_path = REPO / source_id

    assert source_path.is_file()
    source = source_path.read_text(encoding="utf-8")
    result = _inspect(source, source_id=source_id)

    assert result.source_id == source_id
    assert [item.kind for item in result.operations] == [
        "inspect",
        "measure",
    ]


def test_inspect_is_a_non_destructive_diagnostic_view() -> None:
    source_id = "tests/fixtures/observation_contract/inspect_then_measure.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")
    result = _inspect(source, source_id=source_id)

    inspect = result.operations[0]
    assert inspect.semantic_type == "DiagnosticView"
    assert inspect.lane == "diagnostic"
    assert inspect.collapses is False
    assert inspect.preserves_state_lineage is True
    assert inspect.source_node_id


def test_measure_is_the_only_collapsing_terminal_observation() -> None:
    source_id = "tests/fixtures/observation_contract/inspect_then_measure.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")
    result = _inspect(source, source_id=source_id)

    measure = result.operations[1]
    assert measure.semantic_type == "Observation"
    assert measure.observation_kind == "measure"
    assert measure.lane == "terminal_classical"
    assert measure.collapses is True
    assert measure.source_node_id


@pytest.mark.parametrize(
    ("operation", "semantic_type", "collapses"),
    (
        ("expect", "Observable", False),
        ("project", "Projection", False),
        ("trace_out", "State", False),
        ("tomography", "Observation", False),
    ),
)
def test_invalid_observation_fragment_is_rejected_without_fabricated_evidence(
    operation: str, semantic_type: str, collapses: bool
) -> None:
    with pytest.raises(ValueError, match="observation realization unsupported"):
        _inspect(
            f"{operation}(synthetic)",
            source_id=f"synthetic.observation.{operation}.sqx",
        )


def test_unsupported_observation_fails_closed_without_a_fabricated_result() -> None:
    with pytest.raises(ValueError, match="observation realization unsupported"):
        _inspect(
            "unsupported observation",
            source_id="synthetic.observation.unsupported.sqx",
        )
