"""AT-TDD Phase 1 Red: LISS-0459 target capability preflight.

The provider-neutral preflight contract is intentionally absent until this
test-only packet is accepted for Phase 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _api():
    from compiler.staqex.target_preflight import (  # noqa: PLC0415
        CapabilityProfile,
        ResourceDemand,
        preflight_target,
    )

    return CapabilityProfile, ResourceDemand, preflight_target


def _profile(CapabilityProfile, *, calibration_status: str = "declared_only"):
    return CapabilityProfile(
        profile_id="synthetic.ch1",
        profile_version="capability-v1",
        provenance={"kind": "synthetic", "source": "offline-fixture"},
        calibration_status=calibration_status,
        max_logical_qubits=2,
        native_gates=("x", "cx"),
        connectivity=((0, 1),),
        measurement_bases=("computational",),
        reset_supported=False,
        feed_forward_supported=False,
        max_shots=100,
        max_depth=4,
        timing_resolution_ns=10,
        max_payload_bytes=128,
        max_cost_units=5,
    )


def _demand(ResourceDemand, **overrides):
    values = {
        "logical_qubits": 2,
        "gates": ("x",),
        "connectivity": (),
        "measurement_bases": ("computational",),
        "needs_reset": False,
        "needs_feed_forward": False,
        "shots": 10,
        "depth": 1,
        "duration_ns": 10,
        "payload_bytes": 32,
        "cost_units": 1,
    }
    values.update(overrides)
    return ResourceDemand(**values)


def test_profile_preserves_version_provenance_and_nonphysical_calibration() -> None:
    CapabilityProfile, _, _ = _api()
    profile = _profile(CapabilityProfile)

    assert profile.profile_version == "capability-v1"
    assert profile.provenance["kind"] == "synthetic"
    assert profile.calibration_status == "declared_only"
    assert profile.physical_execution_claimed is False


def test_every_unsupported_resource_dimension_rejects_before_allocation() -> None:
    CapabilityProfile, ResourceDemand, preflight_target = _api()
    profile = _profile(CapabilityProfile)
    cases = (
        ("logical_qubits", {"logical_qubits": 3}),
        ("native_gates", {"gates": ("h",)}),
        ("connectivity", {"connectivity": ((0, 2),)}),
        ("measurement_bases", {"measurement_bases": ("x_basis",)}),
        ("reset_supported", {"needs_reset": True}),
        ("feed_forward_supported", {"needs_feed_forward": True}),
        ("max_shots", {"shots": 101}),
        ("max_depth", {"depth": 5}),
        ("timing_resolution_ns", {"duration_ns": 11}),
        ("max_payload_bytes", {"payload_bytes": 129}),
        ("max_cost_units", {"cost_units": 6}),
    )

    for dimension, overrides in cases:
        decision = preflight_target(profile, _demand(ResourceDemand, **overrides))

        assert decision.status == "rejected", dimension
        assert dimension in decision.exceeded_dimensions
        assert decision.allocation is None
        assert decision.artifact is None
        assert decision.provider_payload is None
        assert decision.physical_execution_claimed is False


def test_supported_demand_is_target_ready_but_not_physical_execution_evidence() -> None:
    CapabilityProfile, ResourceDemand, preflight_target = _api()
    profile = _profile(CapabilityProfile)

    decision = preflight_target(profile, _demand(ResourceDemand))

    assert decision.status == "supported"
    assert decision.exceeded_dimensions == ()
    assert decision.profile_version == "capability-v1"
    assert decision.provenance["kind"] == "synthetic"
    assert decision.physical_execution_claimed is False


def test_profile_unknown_or_stale_calibration_is_not_promoted_to_support() -> None:
    CapabilityProfile, ResourceDemand, preflight_target = _api()
    stale = _profile(CapabilityProfile, calibration_status="stale")

    decision = preflight_target(stale, _demand(ResourceDemand))

    assert decision.status == "rejected"
    assert "calibration_status" in decision.exceeded_dimensions
    assert decision.physical_execution_claimed is False


if __name__ == "__main__":
    tests = [
        test_profile_preserves_version_provenance_and_nonphysical_calibration,
        test_every_unsupported_resource_dimension_rejects_before_allocation,
        test_supported_demand_is_target_ready_but_not_physical_execution_evidence,
        test_profile_unknown_or_stale_calibration_is_not_promoted_to_support,
    ]
    for test in tests:
        test()
    print("OK — LISS-0459 Red contract")
