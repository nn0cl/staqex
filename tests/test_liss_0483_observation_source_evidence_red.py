"""Source-owned observation inventory: no fabricated or missing operations."""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.observation_contract import inspect_source
from compiler.staqex.observation_semantic_mapping import map_source
from compiler.staqex.pipeline import compile_source


@pytest.mark.parametrize("operation", ["expect", "project", "trace_out", "tomography"])
def test_invalid_fragment_cannot_fabricate_observation_evidence(operation):
    source = f"{operation}(synthetic)"
    compiled = compile_source(source)
    assert not compiled.ok, compiled.diagnostics
    with pytest.raises(ValueError, match="observation realization unsupported"):
        inspect_source(source, source_id=f"invalid-{operation}.sqx")


def test_real_projection_is_reported_before_terminal_measurement():
    source = """package conformance
pub fn main() -> Unit {
    State psi = 2.0 * |0>
    State projected = project psi onto 0
    Measure projected
}
"""
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    # Finite lowering may remain unavailable; this is a source inventory.
    assert {item["code"] for item in compiled.diagnostics} <= {
        "QSEM_FINITE_EVIDENCE_MISSING",
        "QSEM_APPROXIMATION_OBLIGATION_MISSING",
    }
    result = inspect_source(source, source_id="projection.sqx")
    assert [item.kind for item in result.operations] == ["project", "measure"]
    projection, measurement = result.operations
    assert projection.semantic_type == "Projection"
    assert not projection.collapses
    assert projection.preserves_state_lineage
    assert measurement.collapses
    canonical_ids = {
        node.provenance.source_node_id
        for node in compiled.scientific_semantic_ir.nodes
    }
    assert projection.source_node_id in canonical_ids
    assert measurement.source_node_id in canonical_ids
    assert projection.source_node_id != measurement.source_node_id
    mapped = map_source(source, source_id="projection.sqx")
    assert [item.kind for item in mapped.operations] == ["project", "measure"]
    assert mapped.operations[0].semantic_role == "projection"


@pytest.mark.parametrize(
    ("operation", "semantic_type", "lineage"),
    [("expect", "Observable", False), ("trace_out", "State", True)],
)
def test_real_non_collapsing_observation_calls_are_source_owned(
    operation, semantic_type, lineage
):
    binding = "Float observed = expect(Z, psi)\n    Measure psi" if operation == "expect" else "State observed = trace_out(psi)\n    Measure observed"
    source = f"""package conformance
pub fn main() -> Unit {{
    State psi = |0>
    {binding}
}}
"""
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    contract = inspect_source(source, source_id=f"{operation}.sqx")
    mapped = map_source(source, source_id=f"{operation}.sqx")
    assert contract.operations[0].kind == operation
    assert contract.operations[0].semantic_type == semantic_type
    assert contract.operations[0].collapses is False
    assert contract.operations[0].preserves_state_lineage is lineage
    assert [item.kind for item in mapped.operations] == [operation, "measure"]
    assert mapped.operations[0].collapses is False
