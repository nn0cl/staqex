"""AT-TDD Phase 1 Red: LISS-0077 P0 Dynamic QPU controller contract.

One suite covers lane/escape diagnostics, finite match + one-merge
correlation, reset/reuse capability obligations, and Fake execution under
supplied outcomes. Portable dynamic artifacts, AST parser wire, OpenQASM
dynamic emission, and live adapters are out of scope.
"""

from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _load_api():
    from compiler.staqex.dynamic_qpu import (
        ControllerValue,
        DynamicCapabilityDemand,
        DynamicExecRequest,
        DynamicExecResult,
        FakeDynamicExecutor,
        MatchPlan,
        MergeObligation,
        OutcomeToken,
        verify_dynamic_request,
    )

    return locals()


def _token(api, *, token_id: str = "tok.0", joint_id: str = "joint.0"):
    return api["OutcomeToken"](
        token_id=token_id,
        joint_correlation_id=joint_id,
        outcome_domain=("0", "1"),
    )


def _controller(api, *, name: str = "c0", value: str = "0"):
    return api["ControllerValue"](name=name, value=value, phase="dynamic")


def _demand(
    api,
    *,
    needs_reset: bool = False,
    needs_reuse: bool = False,
    needs_latency: bool = False,
):
    return api["DynamicCapabilityDemand"](
        needs_reset=needs_reset,
        needs_reuse=needs_reuse,
        needs_latency=needs_latency,
    )


def _request(
    api,
    *,
    lane: str = "dynamic",
    profile_id: str = "SIM0_EXACT",
    token=None,
    controllers: tuple = (),
    match_arms: tuple[tuple[str, str], ...] = (("0", "left"), ("1", "right")),
    merge_count: int = 1,
    demand=None,
    supplied_outcomes: dict | None = None,
    escapes_to_theory: bool = False,
    controls_shape: bool = False,
    selects_deployment: bool = False,
):
    token = token if token is not None else _token(api)
    return api["DynamicExecRequest"](
        lane=lane,
        profile_id=profile_id,
        tokens=(token,),
        controllers=controllers if controllers else (_controller(api),),
        match_plan=api["MatchPlan"](token_id=token.token_id, arms=match_arms),
        merge_obligation=api["MergeObligation"](
            joint_correlation_id=token.joint_correlation_id,
            required_merges=1,
            recorded_merges=merge_count,
        ),
        capability_demand=demand if demand is not None else _demand(api),
        supplied_outcomes=supplied_outcomes
        if supplied_outcomes is not None
        else {token.token_id: "0"},
        escapes_to_theory=escapes_to_theory,
        controls_shape=controls_shape,
        selects_deployment=selects_deployment,
    )


def _codes(diagnostics) -> set[str]:
    return {item.code for item in diagnostics}


def test_static_lane_rejects_dynamic_tokens() -> None:
    api = _load_api()
    request = _request(api, lane="static")
    diagnostics = api["verify_dynamic_request"](request)

    assert "DYN_STATIC_LANE_FORBIDDEN" in _codes(diagnostics)


def test_controller_escape_paths_reject() -> None:
    api = _load_api()

    theory = api["verify_dynamic_request"](_request(api, escapes_to_theory=True))
    assert "DYN_THEORY_ESCAPE" in _codes(theory)

    shape = api["verify_dynamic_request"](_request(api, controls_shape=True))
    assert "DYN_SHAPE_CONTROL" in _codes(shape)

    deploy = api["verify_dynamic_request"](_request(api, selects_deployment=True))
    assert "DYN_DEPLOYMENT_SELECTION" in _codes(deploy)


def test_one_merge_correlation_accepts_paired_token() -> None:
    api = _load_api()
    diagnostics = api["verify_dynamic_request"](_request(api, merge_count=1))
    assert diagnostics == []


def test_unpaired_and_double_merge_reject() -> None:
    api = _load_api()
    token = _token(api, token_id="tok.a", joint_id="joint.a")
    unpaired = api["DynamicExecRequest"](
        lane="dynamic",
        profile_id="SIM0_EXACT",
        tokens=(token,),
        controllers=(_controller(api),),
        match_plan=api["MatchPlan"](token_id=token.token_id, arms=(("0", "left"),)),
        merge_obligation=api["MergeObligation"](
            joint_correlation_id="joint.OTHER",
            required_merges=1,
            recorded_merges=1,
        ),
        capability_demand=_demand(api),
        supplied_outcomes={token.token_id: "0"},
        escapes_to_theory=False,
        controls_shape=False,
        selects_deployment=False,
    )
    assert "DYN_UNPAIRED_TOKEN" in _codes(api["verify_dynamic_request"](unpaired))

    double = api["verify_dynamic_request"](_request(api, merge_count=2))
    assert "DYN_DOUBLE_MERGE" in _codes(double)


def test_ch1_profile_rejects_unsupported_latency_only() -> None:
    """LISS-0388 (ADR 0200 Decision 3) repurposed reuse; LISS-0390 (ADR
    0199 Amendment) repurposed reset -- both symmetric for
    simulator-class profiles (CH1_DIGITAL_RESEARCH included). Latency
    alone remains reject-on-demand (ADR 0193 Follow-up #2, still
    deferred).
    """
    api = _load_api()
    request = _request(
        api,
        profile_id="CH1_DIGITAL_RESEARCH",
        demand=_demand(api, needs_reset=True, needs_reuse=True, needs_latency=True),
    )
    codes = _codes(api["verify_dynamic_request"](request))
    assert "DYN_CAPABILITY_RESET" not in codes
    assert "DYN_CAPABILITY_REUSE" not in codes
    assert "DYN_CAPABILITY_LATENCY" in codes


def test_ch1_profile_accepts_reset_alone() -> None:
    """LISS-0390: reset alone (no reuse/latency) is accepted on
    CH1_DIGITAL_RESEARCH, mirroring SIM0_EXACT's repurposed behavior.
    """
    api = _load_api()
    request = _request(
        api,
        profile_id="CH1_DIGITAL_RESEARCH",
        demand=_demand(api, needs_reset=True, needs_reuse=False, needs_latency=False),
    )
    assert api["verify_dynamic_request"](request) == []


def test_ch1_profile_accepts_reuse_alone() -> None:
    """LISS-0388: reuse alone (no reset/latency) is accepted on
    CH1_DIGITAL_RESEARCH, mirroring SIM0_EXACT's repurposed behavior.
    """
    api = _load_api()
    request = _request(
        api,
        profile_id="CH1_DIGITAL_RESEARCH",
        demand=_demand(api, needs_reset=False, needs_reuse=True, needs_latency=False),
    )
    assert api["verify_dynamic_request"](request) == []


def test_sim0_profile_accepts_feedback_without_reset_reuse() -> None:
    api = _load_api()
    diagnostics = api["verify_dynamic_request"](
        _request(api, profile_id="SIM0_EXACT", demand=_demand(api))
    )
    assert diagnostics == []


def test_fake_executor_is_deterministic_under_supplied_outcomes() -> None:
    api = _load_api()
    executor = api["FakeDynamicExecutor"]()
    request = _request(api, supplied_outcomes={"tok.0": "1"})

    first = executor.execute(request)
    second = executor.execute(request)

    assert isinstance(first, api["DynamicExecResult"])
    assert first.status == "accepted"
    assert first.physical_execution_claimed is False
    assert first.selected_arm == "right"
    assert first.consumed_tokens == ("tok.0",)
    assert first.controller_bindings["c0"] == "1"
    assert first == second


def test_fake_executor_rejects_invalid_request_without_fallback() -> None:
    api = _load_api()
    executor = api["FakeDynamicExecutor"]()
    result = executor.execute(_request(api, lane="static"))

    assert result.status == "rejected"
    assert result.physical_execution_claimed is False
    assert result.selected_alternative is None
    assert "DYN_STATIC_LANE_FORBIDDEN" in _codes(result.diagnostics)


def test_controller_value_is_not_state_carrier() -> None:
    api = _load_api()
    controller = _controller(api)
    assert isinstance(controller, api["ControllerValue"])
    assert controller.phase == "dynamic"
    assert not hasattr(controller, "amplitudes")
    assert controller.value in {"0", "1"} or isinstance(controller.value, str)


def test_module_isolation_from_sdk_network_and_semantic_mutation() -> None:
    api = _load_api()
    import compiler.staqex.dynamic_qpu as mod

    text = Path(mod.__file__).read_text(encoding="utf-8")
    forbidden = (
        "qiskit",
        "cirq",
        "pennylane",
        "provider",
        "quantum_semantic_ir",
        "physics_ir",
        "requests",
        "socket",
    )
    for token in forbidden:
        assert token not in text, token
    assert api["FakeDynamicExecutor"] is not None


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
    print(
        f"LISS-0077 integrated Red: {len(tests) - failures} passed, {failures} failed"
    )
    raise SystemExit(1 if failures else 0)
