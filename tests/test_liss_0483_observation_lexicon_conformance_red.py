"""Bounded conformance regressions; no execution or provider support implied."""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source
from compiler.staqex.scientific_lexicon_contract import inspect_source
from compiler.staqex.observation_semantic_mapping import map_source


SOURCE = """package conformance
pub fn main() -> Unit {
    State psi = |+>
    State viewed = Inspect(psi)
    Measure viewed
}
"""


def semantic_nodes(source):
    compiled = compile_source(source)
    # These source-level checks deliberately do not claim finite lowering.
    assert {d["code"] for d in compiled.diagnostics} == {
        "QSEM_FINITE_EVIDENCE_MISSING",
        "QSEM_APPROXIMATION_OBLIGATION_MISSING",
    }
    assert compiled.scientific_semantic_ir is not None
    return compiled.scientific_semantic_ir.nodes


def test_comment_does_not_create_commutator_operation():
    source = "// cm(X, Y) is only a comment\n" + SOURCE
    semantic_nodes(source)
    assert inspect_source(source, source_id="comment.sqx").operations == ()


def test_commutator_display_retains_actual_operands():
    source = SOURCE.replace("    State psi", "    Operator C = cm(Y, Z)\n    State psi")
    semantic_nodes(source)
    operations = inspect_source(source, source_id="operands.sqx").operations
    assert len(operations) == 1
    assert operations[0].display_form == "[Y, Z]"


def test_all_source_commutators_are_reported_in_order():
    source = SOURCE.replace(
        "    State psi",
        "    Operator A = cm(X, Y)\n    Operator B = cm(Y, Z)\n    State psi",
    )
    semantic_nodes(source)
    operations = inspect_source(source, source_id="multiple.sqx").operations
    assert [operation.display_form for operation in operations] == ["[X, Y]", "[Y, Z]"]


def test_invalid_source_cannot_produce_lexicon_bindings():
    source = """package conformance
pub fn main() -> Unit {
    State psi = |0>
    this is not valid Staqex
}
"""
    with pytest.raises(ValueError, match="unsupported scientific spelling"):
        inspect_source(source, source_id="invalid.sqx")


def test_comment_does_not_change_observation_lane_acceptance():
    commented = "// measure as diagnostic is explanatory text\n" + SOURCE
    semantic_nodes(commented)
    baseline = map_source(SOURCE, source_id="same.sqx")
    result = map_source(commented, source_id="same.sqx")
    assert [(op.kind, op.role_lane, op.collapses) for op in result.operations] == [
        (op.kind, op.role_lane, op.collapses) for op in baseline.operations
    ]


@pytest.mark.parametrize("field", ["exactness", "dimensions"])
def test_mapping_retains_semantic_values_including_unknowns(field):
    nodes = {
        node.provenance.source_node_id: node
        for node in semantic_nodes(SOURCE)
        if node.kind in {"Inspect", "Measure"}
    }
    result = map_source(SOURCE, source_id="values.sqx")
    assert len(result.operations) == len(nodes) == 2
    for operation in result.operations:
        canonical = nodes[operation.source_node_id]
        assert getattr(operation, field) == getattr(canonical, field)


def test_mapping_remains_diagnostic_only():
    semantic_nodes(SOURCE)
    result = map_source(SOURCE, source_id="boundary.sqx")
    assert result.semantic_authority == "scientific_semantic_ir"
    assert result.finite_artifact is None
    assert result.provider_payload is None
