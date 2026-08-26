"""AT-TDD Phase 1 Red: LISS-0082 Slice E exactness and finite lowering.

The reviewed boundary is intentionally narrow: Physics IR plus explicit,
source-backed finite-carrier evidence may enter Semantic IR. The lowering
does not Inspect AST/HIR, choose a discretization or encoding, or attach
provider and numerical-plan details.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _load_api():
    from compiler.staqex.quantum_semantic_ir import (
        ActingFactor,
        ActingSpace,
        ApproximationRequired,
        Exact,
        FiniteCarrierEvidence,
        QuantumSemanticInput,
        SemanticId,
        SemanticOrigin,
        lower_physics_to_quantum_semantic_ir,
    )

    return {
        "ActingFactor": ActingFactor,
        "ActingSpace": ActingSpace,
        "ApproximationRequired": ApproximationRequired,
        "Exact": Exact,
        "FiniteCarrierEvidence": FiniteCarrierEvidence,
        "QuantumSemanticInput": QuantumSemanticInput,
        "SemanticId": SemanticId,
        "SemanticOrigin": SemanticOrigin,
        "lower": lower_physics_to_quantum_semantic_ir,
    }


def _identity(api, kind: str, ordinal: int):
    return api["SemanticId"](kind=kind, scope="slice-e.module", ordinal=ordinal)


def _origin(api, *, complete: bool = True):
    return api["SemanticOrigin"](
        source_id="slice-e.staqex" if complete else "",
        line=17 if complete else 0,
        col=3 if complete else 0,
        upstream_ids=("physics.node.0",),
        transform_id="test.slice_e.v1" if complete else "",
    )


def _space(api):
    factors = (
        api["ActingFactor"](
            factor_id=_identity(api, "resource", 0),
            dimension=2,
            label="spin",
        ),
        api["ActingFactor"](
            factor_id=_identity(api, "resource", 1),
            dimension=3,
            label="mode",
        ),
    )
    return api["ActingSpace"](
        space_id=_identity(api, "acting_space", 0),
        factors=factors,
        total_dimension=6,
        origin=_origin(api),
    )


def _finite_evidence(api, space, *, complete: bool = True):
    return api["FiniteCarrierEvidence"](
        evidence_id=_identity(api, "finite_evidence", 0),
        acting_space=space,
        source_kind="source_native",
        origin=_origin(api, complete=complete),
    )


def _input(api, physics_module, *, evidence=(), exactness=()):
    return api["QuantumSemanticInput"](
        physics_module=physics_module,
        finite_carrier_evidence=tuple(evidence),
        linear_resource_evidence=(),
        lane="StaticKernel",
        exactness=tuple(exactness),
    )


def _physics_module():
    from compiler.staqex.physics_ir import PhysicsModule

    return PhysicsModule(spaces=(), nodes=(), origins=())


def _codes(result):
    diagnostics = getattr(result, "diagnostics", result)
    return {diagnostic["code"] for diagnostic in diagnostics}


def test_slice_e_api_is_importable_and_exactness_is_closed():
    api = _load_api()
    exact = api["Exact"]()
    approximation = api["ApproximationRequired"](
        obligation_id=_identity(api, "approximation", 0),
        reason="continuous carrier requires reviewed finite evidence",
        origin=_origin(api),
    )

    assert exact is not None
    assert approximation.reason
    assert not hasattr(approximation, "method")
    assert not hasattr(approximation, "tolerance")
    assert not hasattr(approximation, "resource_estimate")


def test_source_native_finite_evidence_lowers_without_discretization():
    api = _load_api()
    space = _space(api)
    result = api["lower"](
        _input(api, _physics_module(), evidence=(_finite_evidence(api, space),))
    )

    module = result.module
    assert tuple(item.space_id for item in module.acting_spaces) == (space.space_id,)
    assert space.origin in module.origins
    assert "provider" not in repr(module).lower()
    assert "encoding" not in repr(module).lower()


def test_missing_finite_evidence_is_named_and_does_not_fabricate_a_space():
    api = _load_api()
    result = api["lower"](_input(api, _physics_module()))

    assert "QSEM_FINITE_EVIDENCE_MISSING" in _codes(result)
    assert result.module.acting_spaces == ()


def test_incomplete_finite_evidence_preserves_provenance_diagnostic():
    api = _load_api()
    space = _space(api)
    result = api["lower"](
        _input(
            api,
            _physics_module(),
            evidence=(_finite_evidence(api, space, complete=False),),
        )
    )

    assert "QSEM_PROVENANCE_INCOMPLETE" in _codes(result)


def test_approximation_obligation_is_required_without_method_selection():
    api = _load_api()
    space = _space(api)
    obligation = api["ApproximationRequired"](
        obligation_id=_identity(api, "approximation", 0),
        reason="reviewed finite approximation required",
        origin=_origin(api),
    )
    result = api["lower"](
        _input(
            api,
            _physics_module(),
            evidence=(_finite_evidence(api, space),),
            exactness=(obligation,),
        )
    )

    assert result.module.approximation_obligations == (obligation,)
    assert _codes(result) == set()


def test_non_exact_input_without_obligation_is_rejected_without_silent_repair():
    api = _load_api()
    space = _space(api)
    result = api["lower"](
        _input(api, _physics_module(), evidence=(_finite_evidence(api, space),))
    )

    assert "QSEM_APPROXIMATION_OBLIGATION_MISSING" in _codes(result)


if __name__ == "__main__":
    tests = (
        test_slice_e_api_is_importable_and_exactness_is_closed,
        test_source_native_finite_evidence_lowers_without_discretization,
        test_missing_finite_evidence_is_named_and_does_not_fabricate_a_space,
        test_incomplete_finite_evidence_preserves_provenance_diagnostic,
        test_approximation_obligation_is_required_without_method_selection,
        test_non_exact_input_without_obligation_is_rejected_without_silent_repair,
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
