"""AT-TDD Phase 1 Red: LISS-0516 AWS Braket provider fan-out gaps.

These tests use only an injected fake client. They describe the smallest
adapter extension needed to preserve AWS raw lifecycle data and expose a
provider-neutral capability profile for Braket targets.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.adapters.aws_braket import AwsBraketAdapter  # noqa: E402
from compiler.staqex.credentials import EnvCredentialAdapter  # noqa: E402
from compiler.staqex.qpu_contract import (  # noqa: E402
    JobObservationState,
    NormalizedJobState,
)
from compiler.staqex.qpu_submit import ProviderJobId, QpuArtifact, QpuSubmitRequest  # noqa: E402


class FakeBraketFanoutClient:
    """Deterministic fake; no AWS SDK or network access."""

    def __init__(self, state: str) -> None:
        self.state = state

    def create_task(self, qasm: str, device_arn: str, shots: int) -> str:
        return "arn:aws:braket:fake-task-fanout"

    def task_state(self, task_arn: str) -> str:
        return self.state

    def task_result(self, task_arn: str) -> dict:
        return {"measurements": [[0]], "task_arn": task_arn}

    def cancel_task(self, task_arn: str) -> None:
        self.state = "CANCELLED"

    def device_capabilities(self, device_arn: str) -> dict:
        return {
            "provider_name": "IonQ",
            "device_status": "ONLINE",
            "provider_device_id": device_arn,
            "capabilities": ("measure", "openqasm3"),
            "captured_at": datetime.now(timezone.utc),
        }


def _request() -> QpuSubmitRequest:
    return QpuSubmitRequest(
        artifact=QpuArtifact(
            qasm="OPENQASM 3.0;\nqubit q;\nh q;\n",
            target_profile="aws-braket",
            provenance={"source": "test"},
            content_hash="sha256:fanout",
        ),
        execution_settings={"shots": 100},
        idempotency_key="fanout-1",
    )


def _adapter(client: FakeBraketFanoutClient) -> AwsBraketAdapter:
    return AwsBraketAdapter(
        client=client,
        device_arn="arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
        credentials=EnvCredentialAdapter(
            {"AWS_ACCESS_KEY_ID": "fake", "AWS_SECRET_ACCESS_KEY": "fake"}
        ),
    )


def test_status_observation_preserves_cancelling_raw_state() -> None:
    client = FakeBraketFanoutClient("CANCELLING")
    adapter = _adapter(client)
    job_id = adapter.submit(_request())

    status = adapter.status_observation(job_id)

    assert status.provider_state == "CANCELLING"
    assert status.normalized_state == NormalizedJobState.RUNNING
    assert status.observation_state == JobObservationState.OBSERVED
    assert status.terminal is False


def test_status_observation_does_not_guess_unknown_state_as_running() -> None:
    client = FakeBraketFanoutClient("STATE_ADDED_LATER")
    adapter = _adapter(client)
    job_id = ProviderJobId(provider="aws-braket", opaque_id="job-unknown")

    status = adapter.status_observation(job_id)

    assert status.provider_state == "STATE_ADDED_LATER"
    assert status.normalized_state == NormalizedJobState.UNKNOWN
    assert status.terminal is False


def test_legacy_status_fails_closed_for_unknown_state() -> None:
    from compiler.staqex.adapters.aws_braket import BraketUnknownJobStateError

    client = FakeBraketFanoutClient("STATE_ADDED_LATER")
    adapter = _adapter(client)
    job_id = ProviderJobId(provider="aws-braket", opaque_id="job-unknown")

    try:
        adapter.status(job_id)
        assert False, "expected BraketUnknownJobStateError"
    except BraketUnknownJobStateError as exc:
        assert "STATE_ADDED_LATER" in str(exc)


def test_real_client_implements_capability_port_surface() -> None:
    from compiler.staqex.adapters.aws_braket import RealAwsBraketClient

    assert callable(getattr(RealAwsBraketClient, "device_capabilities", None))


def test_capability_profile_separates_route_and_hardware_provider() -> None:
    client = FakeBraketFanoutClient("COMPLETED")
    adapter = _adapter(client)

    profile = adapter.capability_profile()

    assert profile.access_route == "aws-braket"
    assert profile.hardware_provider == "ionq"
    assert profile.device_id.endswith("/ionq/Aria-1")
    assert profile.availability == "online"
    assert profile.capabilities == frozenset({"measure", "openqasm3"})


if __name__ == "__main__":
    tests = [
        test_status_observation_preserves_cancelling_raw_state,
        test_status_observation_does_not_guess_unknown_state_as_running,
        test_legacy_status_fails_closed_for_unknown_state,
        test_real_client_implements_capability_port_surface,
        test_capability_profile_separates_route_and_hardware_provider,
    ]
    failures = []
    for test in tests:
        try:
            test()
        except Exception as error:
            failures.append((test.__name__, error))
    if failures:
        for name, error in failures:
            print(f"FAIL — {name}: {error.__class__.__name__}: {error}")
        raise SystemExit(1)
    print("OK — LISS-0516 Phase 2 Green")
