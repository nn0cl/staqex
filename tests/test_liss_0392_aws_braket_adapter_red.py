"""AT-TDD Phase 1 Red: LISS-0392 AWS Braket Host adapter.

Target: docs/architecture/adr/0202-aws-braket-provider-adapter.md /
LISS-0392.

All tests exercise a fake Braket client. No real network call, no real
AWS credentials, and no real amazon-braket-sdk import are made anywhere
in this file (ADR 0202 Decision 3/5, standing constraint).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.credentials import EnvCredentialAdapter  # noqa: E402
from compiler.staqex.qpu_submit import (  # noqa: E402
    ProviderJobState,
    QpuArtifact,
    QpuSubmitRequest,
)


def _artifact() -> QpuArtifact:
    return QpuArtifact(
        qasm="OPENQASM 3.0;\nqubit q;\nh q;\n",
        target_profile="aws-braket",
        provenance={"source": "test"},
        content_hash="deadbeef",
    )


def _request() -> QpuSubmitRequest:
    return QpuSubmitRequest(
        artifact=_artifact(),
        execution_settings={"shots": 100},
        idempotency_key="idem-1",
    )


class FakeBraketClient:
    """Records calls; returns deterministic fake data. No network."""

    def __init__(self) -> None:
        self.created: list[tuple[str, str, int]] = []
        self.cancelled: list[str] = []
        self._state = "COMPLETED"

    def create_task(self, qasm: str, device_arn: str, shots: int) -> str:
        self.created.append((qasm, device_arn, shots))
        return "arn:aws:braket:fake-task-1"

    def task_state(self, task_arn: str) -> str:
        return self._state

    def task_result(self, task_arn: str) -> dict:
        return {"measurements": [[0, 1], [1, 0]], "task_arn": task_arn}

    def cancel_task(self, task_arn: str) -> None:
        self.cancelled.append(task_arn)
        self._state = "CANCELLED"


def test_submit_fails_closed_when_credentials_missing() -> None:
    from compiler.staqex.adapters.aws_braket import AwsBraketAdapter, BraketCredentialError

    adapter = AwsBraketAdapter(
        client=FakeBraketClient(),
        device_arn="arn:aws:braket::device/fake",
        credentials=EnvCredentialAdapter({}),
    )
    try:
        adapter.submit(_request())
        assert False, "expected BraketCredentialError"
    except BraketCredentialError as exc:
        assert "AWS_ACCESS_KEY_ID" in str(exc)


def test_submit_succeeds_with_credentials_and_delegates_to_client() -> None:
    from compiler.staqex.adapters.aws_braket import AwsBraketAdapter

    client = FakeBraketClient()
    adapter = AwsBraketAdapter(
        client=client,
        device_arn="arn:aws:braket::device/fake",
        credentials=EnvCredentialAdapter(
            {"AWS_ACCESS_KEY_ID": "x", "AWS_SECRET_ACCESS_KEY": "y"}
        ),
    )
    job_id = adapter.submit(_request())

    assert job_id.provider == "aws-braket"
    assert job_id.opaque_id == "arn:aws:braket:fake-task-1"
    assert client.created == [
        (_artifact().qasm, "arn:aws:braket::device/fake", 100)
    ]


def test_submit_accepts_standard_aws_profile_credential_chain() -> None:
    from compiler.staqex.adapters.aws_braket import AwsBraketAdapter

    client = FakeBraketClient()
    adapter = AwsBraketAdapter(
        client=client,
        device_arn="arn:aws:braket::device/fake",
        credentials=EnvCredentialAdapter({"AWS_PROFILE": "developer"}),
    )

    job_id = adapter.submit(_request())

    assert job_id.provider == "aws-braket"
    assert job_id.opaque_id == "arn:aws:braket:fake-task-1"


def test_status_wait_result_cancel_delegate_to_client() -> None:
    from compiler.staqex.adapters.aws_braket import AwsBraketAdapter

    client = FakeBraketClient()
    adapter = AwsBraketAdapter(
        client=client,
        device_arn="arn:aws:braket::device/fake",
        credentials=EnvCredentialAdapter(
            {"AWS_ACCESS_KEY_ID": "x", "AWS_SECRET_ACCESS_KEY": "y"}
        ),
    )
    job_id = adapter.submit(_request())

    assert adapter.status(job_id) == ProviderJobState.SUCCEEDED
    assert adapter.wait(job_id) == ProviderJobState.SUCCEEDED
    result = adapter.result(job_id)
    assert result["task_arn"] == "arn:aws:braket:fake-task-1"

    cancelled_state = adapter.cancel(job_id)
    assert cancelled_state == ProviderJobState.CANCELLED
    assert client.cancelled == ["arn:aws:braket:fake-task-1"]


def test_real_client_refuses_when_sdk_version_is_below_fixed_cve() -> None:
    """CVE-2026-9291 (CVSS 7.1): amazon-braket-sdk < 1.117.0 is vulnerable
    to insecure deserialization in job result processing. The real client
    wrapper must refuse below that version, checked via package metadata
    only (no heavy import needed for this check).
    """
    from compiler.staqex.adapters import aws_braket
    from compiler.staqex.adapters.aws_braket import (
        BraketDependencyError,
        RealAwsBraketClient,
    )

    original = aws_braket._installed_braket_sdk_version
    aws_braket._installed_braket_sdk_version = lambda: "1.100.0"
    try:
        try:
            RealAwsBraketClient()
            assert False, "expected BraketDependencyError"
        except BraketDependencyError as exc:
            assert "CVE-2026-9291" in str(exc)
            assert "1.117.0" in str(exc)
    finally:
        aws_braket._installed_braket_sdk_version = original


def test_real_client_refuses_when_sdk_not_installed() -> None:
    from compiler.staqex.adapters import aws_braket
    from compiler.staqex.adapters.aws_braket import (
        BraketDependencyError,
        RealAwsBraketClient,
    )

    original = aws_braket._installed_braket_sdk_version
    aws_braket._installed_braket_sdk_version = lambda: None
    try:
        try:
            RealAwsBraketClient()
            assert False, "expected BraketDependencyError"
        except BraketDependencyError as exc:
            assert "not installed" in str(exc).lower()
    finally:
        aws_braket._installed_braket_sdk_version = original
