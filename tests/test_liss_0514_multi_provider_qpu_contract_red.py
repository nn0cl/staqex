"""AT-TDD LISS-0514 multi-provider QPU contract.

These tests describe the accepted provider-neutral Host contract.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _api():
    from compiler.staqex.qpu_contract import (  # noqa: PLC0415
        CapabilityFreshnessError,
        CapabilityProfile,
        JobObservationState,
        NormalizedJobState,
        map_provider_job_state,
        preflight_capability,
    )

    return (
        CapabilityFreshnessError,
        CapabilityProfile,
        JobObservationState,
        NormalizedJobState,
        map_provider_job_state,
        preflight_capability,
    )


def test_host_timeout_is_non_terminal_and_preserves_provider_state() -> None:
    _, _, observation_state, normalized_state, map_state, = _api()[:5]

    status = map_state(
        provider_state="RUNNING",
        observation_state=observation_state.TIMED_OUT,
    )

    assert status.provider_state == "RUNNING"
    assert status.normalized_state == normalized_state.RUNNING
    assert status.observation_state == observation_state.TIMED_OUT
    assert status.terminal is False


def test_unknown_provider_state_is_not_guessed_as_failure_or_queue() -> None:
    _, _, observation_state, normalized_state, map_state = _api()[:5]

    status = map_state(
        provider_state="PROVIDER_STATE_ADDED_LATER",
        observation_state=observation_state.OBSERVED,
    )

    assert status.provider_state == "PROVIDER_STATE_ADDED_LATER"
    assert status.normalized_state == normalized_state.UNKNOWN
    assert status.terminal is False


def test_cancelling_state_remains_non_terminal_until_confirmed() -> None:
    _, _, observation_state, normalized_state, map_state = _api()[:5]

    status = map_state(
        provider_state="CANCELLING",
        observation_state=observation_state.OBSERVED,
    )

    assert status.normalized_state == normalized_state.RUNNING
    assert status.terminal is False


def test_expired_capability_fails_closed_before_submission() -> None:
    freshness_error, profile_type, _, _, _, preflight = _api()
    now = datetime.now(timezone.utc)
    profile = profile_type(
        access_route="aws-braket",
        hardware_provider="ionq",
        device_id="arn:aws:braket:::device/qpu/ionq/test",
        profile_fingerprint="profile-v1",
        source="observed",
        availability="online",
        captured_at=now - timedelta(hours=2),
        expires_at=now - timedelta(minutes=1),
        calibration_reference="calibration-v1",
    )

    try:
        preflight(profile, now=now)
    except freshness_error as error:
        assert error.reason == "capability_expired"
    else:
        raise AssertionError("expired capability must fail closed")


def test_fresh_capability_returns_a_submission_snapshot() -> None:
    _, profile_type, _, _, _, preflight = _api()
    now = datetime.now(timezone.utc)
    profile = profile_type(
        access_route="azure-quantum",
        hardware_provider="quantinuum",
        device_id="quantinuum.sim.h1-1sc",
        profile_fingerprint="profile-v2",
        source="observed",
        availability="online",
        captured_at=now - timedelta(minutes=2),
        expires_at=now + timedelta(minutes=10),
        calibration_reference="calibration-v7",
    )

    snapshot = preflight(profile, now=now)

    assert snapshot.profile_fingerprint == "profile-v2"
    assert snapshot.calibration_reference == "calibration-v7"
    assert snapshot.expires_at == profile.expires_at


def test_capability_identity_mismatch_fails_closed() -> None:
    freshness_error, profile_type, _, _, _, preflight = _api()
    now = datetime.now(timezone.utc)
    profile = profile_type(
        access_route="aws-braket",
        hardware_provider="ionq",
        device_id="device-a",
        profile_fingerprint="profile-v3",
        source="observed",
        availability="online",
        captured_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=10),
    )

    try:
        preflight(profile, now=now, expected_device_id="device-b")
    except freshness_error as error:
        assert error.reason == "capability_identity_mismatch"
    else:
        raise AssertionError("identity mismatch must fail closed")


def test_missing_required_capability_fails_closed() -> None:
    freshness_error, profile_type, _, _, _, preflight = _api()
    now = datetime.now(timezone.utc)
    profile = profile_type(
        access_route="azure-quantum",
        hardware_provider="quantinuum",
        device_id="device-h1",
        profile_fingerprint="profile-v4",
        source="observed",
        availability="online",
        captured_at=now - timedelta(minutes=1),
        expires_at=now + timedelta(minutes=10),
        capabilities=frozenset({"measure"}),
    )

    try:
        preflight(
            profile,
            now=now,
            required_capabilities=frozenset({"measure", "dynamic_circuit"}),
        )
    except freshness_error as error:
        assert error.reason == "capability_unsupported"
    else:
        raise AssertionError("missing capability must fail closed")


if __name__ == "__main__":
    tests = [
        test_host_timeout_is_non_terminal_and_preserves_provider_state,
        test_unknown_provider_state_is_not_guessed_as_failure_or_queue,
        test_cancelling_state_remains_non_terminal_until_confirmed,
        test_expired_capability_fails_closed_before_submission,
        test_fresh_capability_returns_a_submission_snapshot,
        test_capability_identity_mismatch_fails_closed,
        test_missing_required_capability_fails_closed,
    ]
    for test in tests:
        test()
    print("OK — LISS-0514 Phase 2 Green")
