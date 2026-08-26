"""AT-TDD Phase 1 Red: LISS-0099 integrated target-capability contract.

One suite covers versioned capability profiles, freshness/unknown handling,
fake physical target ports, CH0/CH1/NH5 fixtures, support/reject decisions
without fallback, IR isolation, and projection into LISS-0092 routing
snapshots. Provider SDKs, credentials, and network calls are absent.
"""

from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _load_api():
    from compiler.staqex.target_capability import (
        CapabilityUnknown,
        FakePhysicalTargetPort,
        Freshness,
        SupportDecision,
        TargetCapabilityProfile,
        evaluate_support,
        project_to_routing_snapshot,
        verify_capability_profile,
    )

    return locals()


def _fresh(api, *, status: str = "fresh", age: str | None = "0s"):
    return api["Freshness"](status=status, age_token=age)


def _unknown(api, name: str, reason: str):
    return api["CapabilityUnknown"](name=name, reason=reason)


def _profile(
    api,
    *,
    profile_id: str = "CH1_DIGITAL_RESEARCH",
    schema_version: str = "1",
    qubits: int = 4,
    freshness=None,
    unknowns: tuple = (),
    max_logical: int | None = None,
    computation_model: str = "digital-gate",
    deployment: str = "local",
    dynamic_supported: bool = False,
    qudit_dimensions: tuple[int, ...] = (2,),
):
    return api["TargetCapabilityProfile"](
        profile_id=profile_id,
        schema_version=schema_version,
        snapshot_id=f"cap.{profile_id.lower()}",
        native_operations=("rz", "sx", "cx"),
        connectivity=tuple((index, index + 1) for index in range(qubits - 1)),
        physical_qubits=tuple(range(qubits)),
        measurement_supported=True,
        reset_supported=True,
        timing_resolution="1ns",
        dynamic_supported=dynamic_supported,
        carrier_kind="qubit",
        computation_model=computation_model,
        qudit_dimensions=qudit_dimensions,
        max_logical_qubits=max_logical if max_logical is not None else qubits,
        max_physical_qubits=qubits,
        max_concurrent_measurements=1,
        deployment_policy=deployment,
        resource_policy="abort-on-exceed",
        power_policy="unknown",
        memory_policy="bounded",
        consent_policy="local-only",
        freshness=freshness if freshness is not None else _fresh(api),
        unknowns=unknowns,
    )


def _codes(diagnostics) -> set[str]:
    return {diagnostic.get("code") for diagnostic in diagnostics}


def test_versioned_profile_distinguishes_capability_dimensions() -> None:
    api = _load_api()
    profile = _profile(api)

    assert profile.schema_version == "1"
    assert profile.native_operations
    assert profile.connectivity
    assert profile.measurement_supported is True
    assert profile.reset_supported is True
    assert profile.timing_resolution == "1ns"
    assert profile.dynamic_supported is False
    assert profile.carrier_kind == "qubit"
    assert profile.computation_model == "digital-gate"
    assert api["verify_capability_profile"](profile) == []


def test_stale_and_unknown_facts_remain_explicit() -> None:
    api = _load_api()
    stale = _profile(
        api,
        freshness=_fresh(api, status="stale", age="30d"),
        unknowns=(_unknown(api, "calibration", "not-fetched"),),
    )

    assert stale.freshness.status == "stale"
    assert stale.unknowns[0].name == "calibration"
    assert stale.unknowns[0].reason == "not-fetched"
    assert "CAPABILITY_STALE" in _codes(api["verify_capability_profile"](stale))

    bare = api["CapabilityUnknown"](name="topology", reason="")
    bad = _profile(api, unknowns=(bare,))
    assert "CAPABILITY_UNKNOWN_REASON_REQUIRED" in _codes(
        api["verify_capability_profile"](bad)
    )


def test_fake_port_loads_shared_ch0_ch1_nh5_schema() -> None:
    api = _load_api()
    port = api["FakePhysicalTargetPort"]()

    ch0 = port.load_profile("CH0_COMMON_PHYSICAL")
    ch1 = port.load_profile("CH1_DIGITAL_RESEARCH")
    nh5 = port.load_profile("NH5_REFERENCE")

    assert isinstance(ch0, api["TargetCapabilityProfile"])
    assert isinstance(ch1, api["TargetCapabilityProfile"])
    assert isinstance(nh5, api["TargetCapabilityProfile"])
    assert ch0.schema_version == ch1.schema_version == nh5.schema_version
    assert {ch0.profile_id, ch1.profile_id, nh5.profile_id} == {
        "CH0_COMMON_PHYSICAL",
        "CH1_DIGITAL_RESEARCH",
        "NH5_REFERENCE",
    }
    assert api["verify_capability_profile"](ch0) == []
    assert api["verify_capability_profile"](ch1) == []
    assert api["verify_capability_profile"](nh5) == []


def test_support_decision_rejects_without_fallback() -> None:
    api = _load_api()
    profile = _profile(api, qubits=2, max_logical=2)
    demand = {"logical_qubits": 8, "needs_dynamic": False}
    decision = api["evaluate_support"](profile, demand)

    assert isinstance(decision, api["SupportDecision"])
    assert decision.status == "rejected"
    assert decision.exceeded_dimensions == ("max_logical_qubits",)
    assert decision.selected_alternative is None


def test_support_decision_accepts_fitting_demand() -> None:
    api = _load_api()
    profile = _profile(api, qubits=4)
    decision = api["evaluate_support"](
        profile, {"logical_qubits": 2, "needs_dynamic": False}
    )

    assert decision.status == "supported"
    assert decision.exceeded_dimensions == ()
    assert decision.selected_alternative is None


def test_dynamic_demand_rejected_when_unsupported() -> None:
    api = _load_api()
    profile = _profile(api, dynamic_supported=False)
    decision = api["evaluate_support"](
        profile, {"logical_qubits": 1, "needs_dynamic": True}
    )

    assert decision.status == "rejected"
    assert decision.exceeded_dimensions == ("dynamic_supported",)
    assert decision.selected_alternative is None


def test_policy_and_model_fields_are_required_on_profiles() -> None:
    api = _load_api()
    profile = _profile(
        api,
        computation_model="digital-gate",
        deployment="local",
        qudit_dimensions=(2, 3),
    )

    assert profile.deployment_policy == "local"
    assert profile.resource_policy == "abort-on-exceed"
    assert profile.consent_policy == "local-only"
    assert profile.qudit_dimensions == (2, 3)
    assert api["verify_capability_profile"](profile) == []

    blank = api["TargetCapabilityProfile"](
        profile_id="CH1_DIGITAL_RESEARCH",
        schema_version="1",
        snapshot_id="cap.blank",
        native_operations=("cx",),
        connectivity=((0, 1),),
        physical_qubits=(0, 1),
        measurement_supported=True,
        reset_supported=True,
        timing_resolution="1ns",
        dynamic_supported=False,
        carrier_kind="",
        computation_model="",
        qudit_dimensions=(),
        max_logical_qubits=2,
        max_physical_qubits=2,
        max_concurrent_measurements=1,
        deployment_policy="",
        resource_policy="",
        power_policy="",
        memory_policy="",
        consent_policy="",
        freshness=_fresh(api),
        unknowns=(),
    )
    codes = _codes(api["verify_capability_profile"](blank))
    assert "CAPABILITY_POLICY_INCOMPLETE" in codes


def test_projection_feeds_liss_0092_routing_pipeline() -> None:
    api = _load_api()
    from compiler.staqex.target_routing import (
        LogicalOperation,
        LogicalResourceId,
        run_target_pipeline,
        verify_target_pipeline,
    )

    profile = _profile(api, profile_id="CH1_DIGITAL_RESEARCH", qubits=4)
    Snapshot = api["project_to_routing_snapshot"](profile)
    plan = {
        "plan_id": "plan.from-capability",
        "resources": (
            LogicalResourceId("q0"),
            LogicalResourceId("q1"),
        ),
        "operations": (
            LogicalOperation(
                "op.h0",
                "h",
                (LogicalResourceId("q0"),),
            ),
            LogicalOperation(
                "op.cx01",
                "cx",
                (LogicalResourceId("q0"), LogicalResourceId("q1")),
            ),
        ),
    }
    result = run_target_pipeline(plan, Snapshot)

    assert result.status == "verified"
    assert verify_target_pipeline(result) == []
    assert Snapshot.profile_id == "CH1_DIGITAL_RESEARCH"


def test_module_does_not_import_physics_or_semantic_ir() -> None:
    api = _load_api()
    import compiler.staqex.target_capability as mod

    assert not hasattr(mod, "PhysicsModule")
    assert not hasattr(mod, "QuantumSemanticModule")
    text = Path(mod.__file__).read_text(encoding="utf-8")
    assert "physics_ir" not in text
    assert "quantum_semantic_ir" not in text
    assert api["FakePhysicalTargetPort"] is not None


def test_fake_port_unknown_profile_fails_closed() -> None:
    api = _load_api()
    port = api["FakePhysicalTargetPort"]()
    try:
        port.load_profile("PROVIDER_LIVE_UNKNOWN")
    except KeyError as error:
        assert "PROVIDER_LIVE_UNKNOWN" in str(error)
        return
    raise AssertionError("unknown profile must fail closed without fallback")


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
        f"LISS-0099 integrated Red: {len(tests) - failures} passed, {failures} failed"
    )
    raise SystemExit(1 if failures else 0)
