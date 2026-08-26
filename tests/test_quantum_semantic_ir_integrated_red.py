"""AT-TDD Phase 1 Red: integrated LISS-0082 Slice E boundary.

This suite intentionally crosses the completed upstream Physics path before
entering Semantic IR. It is one LISS-level Red packet: source -> HIR -> Physics
IR / Equation / Unit / golden evidence -> Semantic lowering -> one verifier.
No production implementation is changed in this phase.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_FIXTURES = _REPO / "tests" / "fixtures" / "physics_ir"


def _load_api():
    from compiler.staqex.physics_ir_goldens import (
        load_physics_ir_goldens,
        verify_golden_against_lowered,
    )
    from compiler.staqex.physics_ir_lower import lower_hir_to_physics_ir
    from compiler.staqex.quantum_semantic_ir import (
        ActingFactor,
        ActingSpace,
        ApproximationRequired,
        Exact,
        FiniteCarrierEvidence,
        LinearResourceEvidence,
        PhysicsEvidenceRef,
        QuantumSemanticInput,
        SemanticId,
        SemanticOrigin,
        lower_physics_to_quantum_semantic_ir,
        verify_quantum_semantic_ir,
    )

    return {
        "load_goldens": load_physics_ir_goldens,
        "verify_golden": verify_golden_against_lowered,
        "lower_physics": lower_hir_to_physics_ir,
        "ActingFactor": ActingFactor,
        "ActingSpace": ActingSpace,
        "ApproximationRequired": ApproximationRequired,
        "Exact": Exact,
        "FiniteCarrierEvidence": FiniteCarrierEvidence,
        "LinearResourceEvidence": LinearResourceEvidence,
        "PhysicsEvidenceRef": PhysicsEvidenceRef,
        "QuantumSemanticInput": QuantumSemanticInput,
        "SemanticId": SemanticId,
        "SemanticOrigin": SemanticOrigin,
        "lower_semantic": lower_physics_to_quantum_semantic_ir,
        "verify_semantic": verify_quantum_semantic_ir,
    }


def _identity(api, kind: str, ordinal: int):
    return api["SemanticId"](kind=kind, scope="slice-e.integrated", ordinal=ordinal)


def _origin(api, *, complete: bool = True):
    return api["SemanticOrigin"](
        source_id="noether-forge.sqx" if complete else "",
        line=23 if complete else 0,
        col=7 if complete else 0,
        upstream_ids=("decl:main", "operator:H"),
        transform_id="liss-0082.slice-e.integrated.v1" if complete else "",
    )


def _source_to_physics(api):
    from compiler.staqex.hir import build_hir
    from compiler.staqex.physics_equation import Coefficient, EquationNode, Unit
    from compiler.staqex.physics_ir import SourceOrigin
    from compiler.staqex.pipeline import compile_source

    compiled = compile_source(
        """
        package noether_forge
        pub fn main() -> Unit {
            Operator H = X + Z
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    assert compiled.unit is not None
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    source_origin = SourceOrigin(source_id="noether-forge.sqx", line=23, col=7)
    unit = Unit(symbol="J", dimensions=(1, 1, -2), origin=source_origin)
    equation = EquationNode(
        kind="dynamics",
        left="H",
        right="omega * N",
        coefficients=(
            Coefficient(expression="omega", unit=unit, origin=source_origin),
        ),
        origin=source_origin,
    )
    physics = api["lower_physics"](
        hir,
        unit=compiled.unit,
        equations=(equation,),
    )
    return physics


def _space(api):
    factors = (
        api["ActingFactor"](
            factor_id=_identity(api, "resource", 0), dimension=2, label="spin"
        ),
        api["ActingFactor"](
            factor_id=_identity(api, "resource", 1), dimension=2, label="mode"
        ),
    )
    return api["ActingSpace"](
        space_id=_identity(api, "acting_space", 0),
        factors=factors,
        total_dimension=4,
        origin=_origin(api),
    )


def _evidence(api, space, *, complete: bool = True):
    physics_refs = (
        api["PhysicsEvidenceRef"](
            physics_node_id="operator:H",
            golden_id="PIR-G-OSCILLATOR-001",
            source_origin=_origin(api, complete=complete),
            review_id="reviewed-fixture-0117",
        ),
    )
    return api["FiniteCarrierEvidence"](
        evidence_id=_identity(api, "finite_evidence", 0),
        acting_space=space,
        physics_refs=physics_refs,
        source_kind="source_native",
        origin=_origin(api, complete=complete),
    )


def _input(api, physics, *, evidence=(), resources=(), exactness=()):
    return api["QuantumSemanticInput"](
        physics_module=physics,
        finite_carrier_evidence=tuple(evidence),
        linear_resource_evidence=tuple(resources),
        lane="StaticKernel",
        exactness=tuple(exactness),
    )


def _codes(result):
    diagnostics = getattr(result, "diagnostics", result)
    return {item["code"] for item in diagnostics}


def test_integrated_source_physics_golden_and_semantic_path_preserves_identity():
    api = _load_api()
    physics = _source_to_physics(api)
    golden = {
        item.golden_id: item for item in api["load_goldens"](_FIXTURES)
    }["PIR-G-OSCILLATOR-001"]
    assert api["verify_golden"](golden, physics) == []

    space = _space(api)
    evidence = _evidence(api, space)
    result = api["lower_semantic"](
        _input(api, physics, evidence=(evidence,), exactness=(api["Exact"](
            operation_id=_identity(api, "operation", 0), origin=_origin(api)
        ),))
    )

    assert result.module.acting_spaces == (space,)
    assert result.module.physics_evidence == (evidence,)
    assert any(node.origin.source_id == "noether-forge.sqx" for node in physics.nodes)
    assert _codes(result) == set()


def test_integrated_lowering_rejects_stale_or_source_mismatched_golden_evidence():
    api = _load_api()
    physics = _source_to_physics(api)
    golden = {
        item.golden_id: item for item in api["load_goldens"](_FIXTURES)
    }["PIR-G-OSCILLATOR-001"]
    space = _space(api)
    evidence = _evidence(api, space)
    stale = api["PhysicsEvidenceRef"](
        physics_node_id="decl:missing",
        golden_id=golden.golden_id,
        source_origin=_origin(api),
        review_id="reviewed-fixture-0117",
    )
    result = api["lower_semantic"](
        _input(api, physics, evidence=(
            api["FiniteCarrierEvidence"](
                evidence_id=evidence.evidence_id,
                acting_space=space,
                physics_refs=(stale,),
                source_kind="source_native",
                origin=evidence.origin,
            ),
        ), exactness=(api["Exact"](
            operation_id=_identity(api, "operation", 0), origin=_origin(api)
        ),))
    )

    assert "QSEM_FINITE_EVIDENCE_INVALID" in _codes(result)


def test_exactness_is_operation_scoped_and_contradictory_markers_are_rejected():
    api = _load_api()
    operation = _identity(api, "operation", 0)
    exact = api["Exact"](operation_id=operation, origin=_origin(api))
    approximate = api["ApproximationRequired"](
        operation_id=operation,
        obligation_id=_identity(api, "approximation", 0),
        reason="reviewed finite approximation",
        origin=_origin(api),
    )
    result = api["lower_semantic"](
        _input(api, _source_to_physics(api), exactness=(exact, approximate))
    )

    assert "QSEM_EXACTNESS_CONFLICT" in _codes(result)


def test_linear_resource_evidence_is_preserved_and_verified_in_one_module():
    api = _load_api()
    resource = api["LinearResourceEvidence"](
        evidence_id=_identity(api, "resource_evidence", 0),
        resource_ids=(_identity(api, "resource", 0),),
        origin=_origin(api),
    )
    result = api["lower_semantic"](
        _input(api, _source_to_physics(api), resources=(resource,))
    )

    assert result.module.linear_resource_evidence == (resource,)
    assert "QSEM_RESOURCE_EVIDENCE_INVALID" not in _codes(result)


def test_nested_provenance_and_upstream_resolution_are_closed():
    api = _load_api()
    space = _space(api)
    incomplete = _evidence(api, space, complete=False)
    result = api["lower_semantic"](
        _input(api, _source_to_physics(api), evidence=(incomplete,))
    )

    assert "QSEM_PROVENANCE_INCOMPLETE" in _codes(result)
    assert "QSEM_PROVENANCE_UNRESOLVED" in _codes(result)


def test_lowering_runs_the_single_semantic_verifier_without_repair():
    api = _load_api()
    invalid_space = api["ActingSpace"](
        space_id=_identity(api, "acting_space", 0),
        factors=(),
        total_dimension=0,
        origin=_origin(api),
    )
    evidence = api["FiniteCarrierEvidence"](
        evidence_id=_identity(api, "finite_evidence", 0),
        acting_space=invalid_space,
        physics_refs=(),
        source_kind="source_native",
        origin=_origin(api),
    )
    result = api["lower_semantic"](
        _input(api, _source_to_physics(api), evidence=(evidence,))
    )

    assert "QSEM_ACTING_SPACE_INVALID" in _codes(result)
    assert result.module.acting_spaces == (invalid_space,)
    assert api["verify_semantic"](result.module)


def test_semantic_lowering_rejects_raw_ast_or_hir_input():
    api = _load_api()
    from compiler.staqex.hir import build_hir
    from compiler.staqex.pipeline import compile_source

    compiled = compile_source("package t\npub fn main() -> Unit { Measure Coin() }")
    assert compiled.checker is not None
    assert compiled.unit is not None
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )

    try:
        api["lower_semantic"](hir)
    except TypeError as exc:
        assert "QuantumSemanticInput" in str(exc)
    else:
        raise AssertionError("raw HIR must not enter Semantic lowering")


if __name__ == "__main__":
    tests = (
        test_integrated_source_physics_golden_and_semantic_path_preserves_identity,
        test_integrated_lowering_rejects_stale_or_source_mismatched_golden_evidence,
        test_exactness_is_operation_scoped_and_contradictory_markers_are_rejected,
        test_linear_resource_evidence_is_preserved_and_verified_in_one_module,
        test_nested_provenance_and_upstream_resolution_are_closed,
        test_lowering_runs_the_single_semantic_verifier_without_repair,
        test_semantic_lowering_rejects_raw_ast_or_hir_input,
    )

    failures = 0
    for test in tests:
        try:
            test()
        except Exception as error:
            failures += 1
            print(f"FAIL {test.__name__}: {error}")
        else:
            print(f"pass {test.__name__}")

    print(f"\n{len(tests) - failures} passed, {failures} failed")
    sys.exit(1 if failures else 0)
