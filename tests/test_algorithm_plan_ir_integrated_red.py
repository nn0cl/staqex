"""AT-TDD Phase 1 Red: LISS-0083 integrated Algorithm Plan IR contract.

This is one Red suite for the six internal review dimensions of LISS-0083.
It deliberately uses provider-neutral records and deterministic literals. No
algorithm implementation, pass manager, provider SDK, gate emitter, or
numeric solver is part of this phase.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _load_api():
    from compiler.staqex.algorithm_plan_ir import (
        AlgorithmPlanModule,
        ApproximationObligation,
        ConsumerProjection,
        PlanNode,
        PlanOrigin,
        RealizationDecision,
        ResourceExpr,
        project_algorithm_plan,
        verify_algorithm_plan,
    )

    return locals()


def _origin(api, *, complete=True):
    return api["PlanOrigin"](
        source_id="noether-forge.staqex",
        physics_id="physics.module.0",
        upstream_ids=("semantic.operation.0",) if complete else (),
        transform_id="plan.red.v1" if complete else "",
    )


def _obligation(api, *, status="closed", bound="1/100", disposition="accepted"):
    return api["ApproximationObligation"](
        obligation_id="obligation.0",
        status=status,
        bound=bound,
        estimate=None,
        disposition=disposition,
    )


def _decision(api, *, complete=True):
    return api["RealizationDecision"](
        decision_id="decision.0",
        kind="mapping",
        selected="symbolic-jordan-wigner",
        alternatives=("bravyi-kitaev", "parity").__getitem__(slice(None)),
        assumptions=("finite-local-dimension",) if complete else (),
        rejection_reasons=("not selected for current witness",) if complete else (),
        policy_provenance="policy.mapping.v1" if complete else "",
    )


def _resources(api):
    return api["ResourceExpr"](
        resource_id="resource.0",
        logical_dimensions=("2**4096",),
        ancillas="2**2048",
        depth="3*n",
        operations="n*(n-1)/2",
        measurements="n",
        classical_latency="symbolic:latency(n)",
        simulator_memory="2**4096",
        target_materialization="deferred",
        multiplicity="2**4096",
    )


def _node(api, *, complete=True):
    return api["PlanNode"](
        node_id="plan.node.0",
        semantic_id="semantic.operation.0",
        origin=_origin(api, complete=complete),
        exactness="approximate",
        obligation_id="obligation.0",
        decision_ids=("decision.0",),
        resource_id="resource.0",
        operation_kind="Evolve",
    )


def _module(api, *, node=None, obligation=None, decision=None, resources=None):
    return api["AlgorithmPlanModule"](
        schema_version=1,
        plan_id="plan.0",
        nodes=(node if node is not None else _node(api),),
        obligations=(
            obligation if obligation is not None else _obligation(api),
        ),
        decisions=(decision if decision is not None else _decision(api),),
        resources=(resources if resources is not None else _resources(api),),
        repetitions=("callable-region.0",),
        witnesses=("SIM0_EXACT", "NH5", "QP-2", "QS-2"),
    )


def _codes(diagnostics) -> set[str]:
    return {diagnostic.get("code") for diagnostic in diagnostics}


def test_integrated_exact_and_bounded_approximate_plans_verify() -> None:
    api = _load_api()
    exact = _module(
        api,
        node=api["PlanNode"](
            node_id="plan.node.exact",
            semantic_id="semantic.operation.exact",
            origin=_origin(api),
            exactness="exact",
            obligation_id=None,
            decision_ids=(),
            resource_id="resource.0",
            operation_kind="prepare",
        ),
    )
    assert api["verify_algorithm_plan"](exact) == []
    assert api["verify_algorithm_plan"](_module(api)) == []


def test_missing_provenance_is_rejected() -> None:
    api = _load_api()
    diagnostics = api["verify_algorithm_plan"](
        _module(api, node=_node(api, complete=False))
    )
    assert "ALGORITHM_PLAN_PROVENANCE_INCOMPLETE" in _codes(diagnostics)


def test_approximation_requires_bound_and_disposition() -> None:
    api = _load_api()
    diagnostics = api["verify_algorithm_plan"](
        _module(
            api,
            obligation=_obligation(api, bound=None, disposition=""),
        )
    )
    assert "ALGORITHM_PLAN_APPROXIMATION_INVALID" in _codes(diagnostics)


def test_unresolved_obligation_cannot_be_presented_as_closed() -> None:
    api = _load_api()
    diagnostics = api["verify_algorithm_plan"](
        _module(api, obligation=_obligation(api, status="unresolved"))
    )
    assert "ALGORITHM_PLAN_OBLIGATION_UNCLOSED" in _codes(diagnostics)


def test_realization_choice_requires_policy_evidence_and_alternatives() -> None:
    api = _load_api()
    diagnostics = api["verify_algorithm_plan"](
        _module(api, decision=_decision(api, complete=False))
    )
    assert "ALGORITHM_PLAN_REALIZATION_INVALID" in _codes(diagnostics)


def test_symbolic_resources_are_preserved_without_eager_expansion() -> None:
    api = _load_api()
    module = _module(api)
    assert module.resources[0].multiplicity == "2**4096"
    assert module.resources[0].target_materialization == "deferred"
    assert api["verify_algorithm_plan"](module) == []


def test_projection_is_consumer_neutral_and_does_not_mutate_source() -> None:
    api = _load_api()
    module = _module(api)
    before = module
    projection = api["project_algorithm_plan"](
        module,
        api["ConsumerProjection"](
            consumer="SIM0_EXACT",
            plan_id="plan.0",
            requested_fields=("resources", "obligations"),
        ),
    )
    assert projection.consumer == "SIM0_EXACT"
    assert module is before
    assert api["verify_algorithm_plan"](module) == []


def test_runtime_adaptive_choice_and_provider_fields_are_rejected() -> None:
    api = _load_api()
    adaptive = api["RealizationDecision"](
        decision_id="decision.0",
        kind="measurement",
        selected="runtime-selected",
        alternatives=("provider.sdk.gate",),
        assumptions=("runtime feedback",),
        rejection_reasons=("",),
        policy_provenance="",
    )
    diagnostics = api["verify_algorithm_plan"](_module(api, decision=adaptive))
    assert "ALGORITHM_PLAN_POLICY_INVALID" in _codes(diagnostics)


def test_current_and_horizon_witnesses_use_one_compact_schema() -> None:
    api = _load_api()
    module = _module(api)
    assert set(module.witnesses) == {"SIM0_EXACT", "NH5", "QP-2", "QS-2"}
    assert len(module.repetitions) == 1
    assert api["verify_algorithm_plan"](module) == []


def test_diagnostics_are_canonical_and_deterministic() -> None:
    api = _load_api()
    broken = _module(
        api,
        node=_node(api, complete=False),
        obligation=_obligation(api, bound=None, disposition=""),
        decision=_decision(api, complete=False),
    )
    first = api["verify_algorithm_plan"](broken)
    second = api["verify_algorithm_plan"](broken)
    assert first == second
    assert [item.get("code") for item in first] == sorted(
        item.get("code") for item in first
    )


if __name__ == "__main__":
    tests = (
        test_integrated_exact_and_bounded_approximate_plans_verify,
        test_missing_provenance_is_rejected,
        test_approximation_requires_bound_and_disposition,
        test_unresolved_obligation_cannot_be_presented_as_closed,
        test_realization_choice_requires_policy_evidence_and_alternatives,
        test_symbolic_resources_are_preserved_without_eager_expansion,
        test_projection_is_consumer_neutral_and_does_not_mutate_source,
        test_runtime_adaptive_choice_and_provider_fields_are_rejected,
        test_current_and_horizon_witnesses_use_one_compact_schema,
        test_diagnostics_are_canonical_and_deterministic,
    )

    failures = 0
    for test in tests:
        try:
            test()
        except Exception as error:
            failures += 1
            print(f"FAIL {test.__name__}: {type(error).__name__}: {error}")
        else:
            print(f"pass {test.__name__}")

    print(f"\n{len(tests) - failures} passed, {failures} failed")
    sys.exit(1 if failures else 0)
