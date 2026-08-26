"""Phase 1 Red contracts for canonical semantic meaning preservation."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_path


FIXTURE = REPO / "tests/fixtures/semantic_meaning/mixture_and_product.sqx"


def test_mixture_and_product_remain_distinct_structural_meanings() -> None:
    compiled = compile_path(FIXTURE)
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    nodes = compiled.scientific_semantic_ir.nodes
    mixture = next(node for node in nodes if node.kind == "WhenExpr")
    product = next(node for node in nodes if node.kind == "OpBin")
    assert mixture.meaning_kind == "mixture"
    assert product.meaning_kind == "mathematical_product"


def test_mixture_preserves_children_state_role_and_provenance() -> None:
    compiled = compile_path(FIXTURE)
    assert compiled.scientific_semantic_ir is not None
    mixture = next(node for node in compiled.scientific_semantic_ir.nodes if node.kind == "WhenExpr")
    assert mixture.state_role == "mixed_state"
    assert mixture.child_source_node_ids
    assert mixture.provenance.source_node_id == mixture.node_id


def test_missing_target_projection_does_not_erase_ideal_meaning() -> None:
    compiled = compile_path(FIXTURE)
    assert compiled.scientific_semantic_ir is not None
    assert compiled.unit is not None
    from compiler.staqex.backend.qasm.lower import EvolutionTargetProfile, lower_unit_to_circuit

    circuit = lower_unit_to_circuit(compiled.unit, target_profile=EvolutionTargetProfile())
    assert circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert compiled.scientific_semantic_ir.ideal_meaning is not None
    assert compiled.scientific_semantic_ir.ideal_meaning.source_fingerprint


def test_exact_exponential_is_exact_and_unrelated_binder_does_not_authorize_it() -> None:
    from compiler.staqex.backend.qasm.lower import EvolutionTargetProfile, lower_unit_to_circuit
    from compiler.staqex.pipeline import compile_source

    compiled = compile_source(
        """
        package fixtures.semantic_meaning
        pub fn main() -> Unit {
            Operator H = X
            Operator unrelated = Sigma (i In 0..1) { Z[i] }
            Operator U = exp(-i * H)
            State psi = |0>
            State result = Evolve() { U * psi }.run()
            Measure result
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    exact = next(
        node
        for node in compiled.scientific_semantic_ir.nodes
        if node.kind == "ExactExponential"
    )
    assert exact.exactness == "exact"
    circuit = lower_unit_to_circuit(
        compiled.unit,
        target_profile=EvolutionTargetProfile(
            suzuki_order=2,
            suzuki_steps=1,
            realization_mode="approximate",
            resource_budget_qubits=4,
        ),
    )
    assert circuit.reject_code == "E_QPU_CANONICAL_FINITE_EVOLUTION_UNSUPPORTED"
    assert circuit.gates == []
    assert circuit.n_qubits == 0
    assert circuit.allocation_started is False


if __name__ == "__main__":
    for test in (
        test_mixture_and_product_remain_distinct_structural_meanings,
        test_mixture_preserves_children_state_role_and_provenance,
        test_missing_target_projection_does_not_erase_ideal_meaning,
        test_exact_exponential_is_exact_and_unrelated_binder_does_not_authorize_it,
    ):
        test()
