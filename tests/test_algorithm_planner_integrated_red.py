"""AT-TDD Phase 1 Red: LISS-0088 integrated planner contract.

The suite fixes the provider-neutral planner boundary before implementation.
It deliberately uses repository-local literals and no provider, simulator,
network, random source, or numerical solver.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _load_api():
    from compiler.staqex.algorithm_planner import (  # type: ignore
        AlgorithmCandidate,
        CandidateEvaluation,
        PlannerDecision,
        PlannerProfile,
        PlannerRequest,
        PreparationContract,
        plan_algorithm,
    )

    return locals()


def _profile(api, name="SIM0_EXACT"):
    return api["PlannerProfile"](
        profile_id=name,
        resource_envelope=("active_qubits<=20", "symbolic_depth_allowed"),
    )


def _request(api, *, profile="SIM0_EXACT", provenance=True):
    return api["PlannerRequest"](
        request_id="request.h2.0",
        hamiltonian_id="physics.hamiltonian.h2",
        observable_ids=("physics.observable.energy",),
        provenance=("source.h2", "physics.h2", "semantic.h2") if provenance else (),
        operation="evolve",
        profile=api["PlannerProfile"](
            profile_id=profile,
            resource_envelope=("active_qubits<=20", "symbolic_depth_allowed"),
        ),
        constraints=("preserve_joint_state", "no_provider_selection"),
    )


def _candidate(api, *, family="suzuki", exactness="approximate", supported=True):
    return api["AlgorithmCandidate"](
        candidate_id=f"candidate.{family}",
        family=family,
        exactness=exactness,
        parameters=("order=2", "steps=symbolic"),
        prerequisites=("finite_pauli_terms",) if supported else ("ft_qec",),
    )


def _evaluation(api, *, closed=True):
    return api["CandidateEvaluation"](
        evaluation_id="evaluation.0",
        disposition="accepted",
        alternatives=("qdrift", "krylov"),
        assumptions=("finite_pauli_terms",),
        rejection_reasons=("qdrift variance exceeds witness budget",),
        policy_provenance="planner.policy.p1.v1",
        approximation_bound="1/100" if closed else None,
        resource_expression="steps * pauli_terms" if closed else "",
    )


def _preparation(api, *, explicit=True):
    return api["PreparationContract"](
        preparation_id="preparation.h2.0",
        source="declared_state.h2" if explicit else "",
        obligations=("source_verified",) if explicit else (),
        assumes_zero_state=not explicit,
        assumes_oracle=not explicit,
    )


def _decision(api, **overrides):
    values = dict(
        request=_request(api),
        candidate=_candidate(api),
        evaluation=_evaluation(api),
        preparation=_preparation(api),
    )
    values.update(overrides)
    return api["PlannerDecision"](**values)


def test_exact_suzuki_candidate_is_accepted() -> None:
    api = _load_api()
    decision = _decision(
        api,
        request=_request(api, profile="SIM0_EXACT"),
        candidate=_candidate(api, exactness="exact"),
    )
    result = api["plan_algorithm"](decision)
    assert result.disposition == "accepted"
    assert result.selected_family == "suzuki"


def test_bounded_suzuki_closes_approximation_and_resource_obligations() -> None:
    api = _load_api()
    result = api["plan_algorithm"](_decision(api))
    assert result.approximation_bound == "1/100"
    assert result.resource_expression == "steps * pauli_terms"


def test_qdrift_uses_the_same_closed_evidence_contract() -> None:
    api = _load_api()
    result = api["plan_algorithm"](
        _decision(api, candidate=_candidate(api, family="qdrift"))
    )
    assert result.disposition == "accepted"
    assert result.policy_provenance == "planner.policy.p1.v1"


def test_hardware_efficient_preparation_requires_explicit_state_evidence() -> None:
    api = _load_api()
    result = api["plan_algorithm"](
        _decision(
            api,
            candidate=_candidate(api, family="hardware_efficient_preparation"),
            preparation=_preparation(api),
        )
    )
    assert result.disposition == "accepted"
    assert result.preparation_source == "declared_state.h2"


def test_incomplete_provenance_is_rejected() -> None:
    api = _load_api()
    result = api["plan_algorithm"](
        _decision(api, request=_request(api, provenance=False))
    )
    assert "PLANNER_PROVENANCE_INCOMPLETE" in result.diagnostic_codes


def test_approximate_candidate_requires_bound_and_resource_evidence() -> None:
    api = _load_api()
    result = api["plan_algorithm"](
        _decision(api, evaluation=_evaluation(api, closed=False))
    )
    assert "PLANNER_APPROXIMATION_INVALID" in result.diagnostic_codes


def test_decision_requires_alternatives_assumptions_rejections_and_policy() -> None:
    api = _load_api()
    incomplete = api["CandidateEvaluation"](
        evaluation_id="evaluation.incomplete",
        disposition="accepted",
        alternatives=(),
        assumptions=(),
        rejection_reasons=(),
        policy_provenance="",
        approximation_bound="1/100",
        resource_expression="steps",
    )
    result = api["plan_algorithm"](_decision(api, evaluation=incomplete))
    assert "PLANNER_DECISION_EVIDENCE_INVALID" in result.diagnostic_codes


def test_zero_state_and_oracle_assumptions_are_rejected() -> None:
    api = _load_api()
    result = api["plan_algorithm"](
        _decision(api, preparation=_preparation(api, explicit=False))
    )
    assert "PLANNER_PREPARATION_INVALID" in result.diagnostic_codes


def test_runtime_adaptive_and_provider_specific_policy_is_rejected() -> None:
    api = _load_api()
    candidate = _candidate(api)
    evaluation = api["CandidateEvaluation"](
        evaluation_id="evaluation.provider",
        disposition="accepted",
        alternatives=("provider.sdk.gate",),
        assumptions=("runtime feedback",),
        rejection_reasons=("",),
        policy_provenance="",
        approximation_bound="1/100",
        resource_expression="steps",
    )
    result = api["plan_algorithm"](
        _decision(api, candidate=candidate, evaluation=evaluation)
    )
    assert "PLANNER_POLICY_INVALID" in result.diagnostic_codes


def test_deferred_methods_remain_explicitly_unsupported() -> None:
    api = _load_api()
    result = api["plan_algorithm"](
        _decision(
            api,
            candidate=_candidate(api, family="qubitization", supported=False),
            evaluation=api["CandidateEvaluation"](
                evaluation_id="evaluation.deferred",
                disposition="unsupported",
                alternatives=("suzuki",),
                assumptions=("fault_tolerant_qec_required",),
                rejection_reasons=("P2 prerequisite not accepted",),
                policy_provenance="planner.policy.p2-gate.v1",
                approximation_bound=None,
                resource_expression="logical_oracles",
            ),
        )
    )
    assert result.disposition == "unsupported"
    assert result.rejection_reasons == ("P2 prerequisite not accepted",)


def test_symbolic_profiles_share_one_compact_decision_shape() -> None:
    api = _load_api()
    results = []
    for profile in ("SIM0_EXACT", "CH1_DIGITAL_RESEARCH", "NH5_NISQ_MODULAR"):
        results.append(
            api["plan_algorithm"](
                _decision(api, request=_request(api, profile=profile))
            )
        )
    assert [result.selected_family for result in results] == ["suzuki"] * 3
    assert all(result.resource_expression == "steps * pauli_terms" for result in results)


def test_diagnostics_and_serialization_are_deterministic() -> None:
    api = _load_api()
    broken = _decision(
        api,
        request=_request(api, provenance=False),
        evaluation=_evaluation(api, closed=False),
        preparation=_preparation(api, explicit=False),
    )
    first = api["plan_algorithm"](broken)
    second = api["plan_algorithm"](broken)
    assert first.diagnostic_codes == second.diagnostic_codes
    assert first.to_dict() == second.to_dict()


if __name__ == "__main__":
    tests = tuple(
        value
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
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
    raise SystemExit(1 if failures else 0)
