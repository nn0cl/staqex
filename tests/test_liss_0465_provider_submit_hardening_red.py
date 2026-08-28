"""AT-TDD Phase 1 Red: LISS-0465 provider-neutral submit hardening."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.qpu_submit import (  # noqa: E402
    ProviderJobId,
    QpuArtifact,
    QpuSubmitRequest,
)


def _api():
    from compiler.staqex.submit_integration import (  # noqa: PLC0415
        SubmitIntegrationPolicy,
        submit_artifact,
    )

    return SubmitIntegrationPolicy, submit_artifact


class FakeProviderPort:
    def __init__(self, *, failure: Exception | None = None) -> None:
        self.calls: list[QpuSubmitRequest] = []
        self.failure = failure

    def submit(self, request: QpuSubmitRequest) -> ProviderJobId:
        self.calls.append(request)
        if self.failure:
            raise self.failure
        return ProviderJobId(provider="fake", opaque_id=f"job-{request.idempotency_key}")


def _request(**settings) -> QpuSubmitRequest:
    return QpuSubmitRequest(
        artifact=QpuArtifact(
            qasm="OPENQASM 3.0;\nqubit q;\nh q;\n",
            target_profile="fake-qpu",
            provenance={"source_fingerprint": "sha256:source"},
            content_hash="sha256:artifact",
        ),
        execution_settings={"shots": 100, **settings},
        idempotency_key="request-1",
    )


def test_submit_preserves_identity_and_reuses_same_idempotency_request() -> None:
    Policy, submit_artifact = _api()
    provider = FakeProviderPort()
    policy = Policy(max_qasm_bytes=1024, allowed_targets=("fake-qpu",))

    first = submit_artifact(_request(), provider=provider, policy=policy)
    second = submit_artifact(_request(), provider=provider, policy=policy)

    assert first.status == "submitted"
    assert second.status == "deduplicated"
    assert first.job_id == second.job_id
    assert len(provider.calls) == 1
    sent = provider.calls[0]
    assert sent.idempotency_key == "request-1"
    assert sent.artifact.target_profile == "fake-qpu"
    assert sent.artifact.content_hash == "sha256:artifact"
    assert sent.execution_settings["shots"] == 100


def test_dry_run_performs_zero_submit_calls() -> None:
    Policy, submit_artifact = _api()
    provider = FakeProviderPort()

    result = submit_artifact(
        _request(),
        provider=provider,
        policy=Policy(max_qasm_bytes=1024, allowed_targets=("fake-qpu",)),
        mode="dry-run",
    )

    assert result.status == "dry-run"
    assert result.job_id is None
    assert provider.calls == []


def test_unsupported_payload_is_rejected_before_provider_invocation() -> None:
    Policy, submit_artifact = _api()
    provider = FakeProviderPort()
    result = submit_artifact(
        _request(),
        provider=provider,
        policy=Policy(max_qasm_bytes=4, allowed_targets=("other-qpu",)),
    )

    assert result.status == "rejected"
    assert "PAYLOAD_UNSUPPORTED" in result.diagnostic_codes
    assert "TARGET_UNSUPPORTED" in result.diagnostic_codes
    assert result.job_id is None
    assert provider.calls == []


def test_transient_and_permanent_provider_failures_are_typed_and_not_retried_implicitly() -> None:
    Policy, submit_artifact = _api()
    policy = Policy(max_qasm_bytes=1024, allowed_targets=("fake-qpu",))

    transient_provider = FakeProviderPort(failure=TimeoutError("provider timeout"))
    transient = submit_artifact(_request(), provider=transient_provider, policy=policy)
    assert transient.status == "transient-failure"
    assert transient.retryable is True
    assert len(transient_provider.calls) == 1

    permanent_provider = FakeProviderPort(failure=ValueError("invalid payload"))
    permanent = submit_artifact(_request(), provider=permanent_provider, policy=policy)
    assert permanent.status == "permanent-failure"
    assert permanent.retryable is False
    assert len(permanent_provider.calls) == 1


if __name__ == "__main__":
    tests = [
        test_submit_preserves_identity_and_reuses_same_idempotency_request,
        test_dry_run_performs_zero_submit_calls,
        test_unsupported_payload_is_rejected_before_provider_invocation,
        test_transient_and_permanent_provider_failures_are_typed_and_not_retried_implicitly,
    ]
    for test in tests:
        test()
    print("OK — LISS-0465 Red contract")
