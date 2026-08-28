"""AT-TDD Phase 1 Red: LISS-0466 job lifecycle/result integrity."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.qpu_submit import ProviderJobId, ProviderJobState  # noqa: E402


def _api():
    from compiler.staqex.job_lifecycle import (  # noqa: PLC0415
        JobLifecyclePolicy,
        observe_job,
    )

    return JobLifecyclePolicy, observe_job


class FakeJobPort:
    def __init__(self, state: ProviderJobState, payload: dict | None = None) -> None:
        self.state = state
        self.payload = payload or {}
        self.status_calls = 0
        self.result_calls = 0
        self.cancel_calls = 0
        self.submit_calls = 0

    def status(self, job_id: ProviderJobId) -> ProviderJobState:
        self.status_calls += 1
        return self.state

    def wait(self, job_id: ProviderJobId) -> ProviderJobState:
        return self.status(job_id)

    def result(self, job_id: ProviderJobId) -> dict:
        self.result_calls += 1
        return self.payload

    def cancel(self, job_id: ProviderJobId) -> ProviderJobState:
        self.cancel_calls += 1
        self.state = ProviderJobState.CANCELLED
        return self.state


def _job() -> ProviderJobId:
    return ProviderJobId(provider="fake", opaque_id="job-1")


def _metadata() -> dict[str, str]:
    return {
        "source_fingerprint": "sha256:source",
        "semantic_fingerprint": "sha256:semantic",
        "artifact_fingerprint": "sha256:artifact",
    }


def test_successful_result_preserves_metadata_and_attempt_order() -> None:
    Policy, observe_job = _api()
    port = FakeJobPort(
        ProviderJobState.SUCCEEDED,
        {"measurements": ({"output": "0", "value": 1},), "attempt": 2},
    )
    result = observe_job(
        _job(),
        job_port=port,
        policy=Policy(expected_measurements=("0",)),
        metadata={**_metadata(), "attempt": 2},
    )

    assert result.status == "succeeded"
    assert result.metadata == {**_metadata(), "attempt": 2}
    assert result.measurements[0]["output"] == "0"
    assert result.attempt == 2


def test_partial_result_is_failed_and_never_presented_as_success() -> None:
    Policy, observe_job = _api()
    port = FakeJobPort(
        ProviderJobState.SUCCEEDED,
        {"measurements": ({"output": "0", "value": 1},)},
    )
    result = observe_job(
        _job(),
        job_port=port,
        policy=Policy(expected_measurements=("0", "1")),
        metadata=_metadata(),
    )

    assert result.status == "failed"
    assert "QPU_RESULT_INCOMPLETE" in result.diagnostic_codes
    assert result.measurements == ()


def test_failed_cancelled_timeout_and_unknown_states_are_distinct() -> None:
    Policy, observe_job = _api()
    policy = Policy(expected_measurements=())
    for state, expected in (
        (ProviderJobState.FAILED, "failed"),
        (ProviderJobState.CANCELLED, "cancelled"),
        (ProviderJobState.QUEUED, "timeout"),
    ):
        result = observe_job(
            _job(),
            job_port=FakeJobPort(state),
            policy=policy,
            metadata=_metadata(),
            timeout_polls=1,
        )
        assert result.status == expected
        assert result.measurements == ()

    unknown = observe_job(
        _job(),
        job_port=FakeJobPort("BROKEN"),  # type: ignore[arg-type]
        policy=policy,
        metadata=_metadata(),
    )
    assert unknown.status == "failed"
    assert "QPU_STATE_UNKNOWN" in unknown.diagnostic_codes


def test_cancel_is_explicit_and_polling_does_not_resubmit() -> None:
    Policy, observe_job = _api()
    port = FakeJobPort(ProviderJobState.CANCELLED)
    result = observe_job(
        _job(),
        job_port=port,
        policy=Policy(expected_measurements=()),
        metadata={**_metadata(), "cancel_requested": True},
    )

    assert result.status == "cancelled"
    assert port.cancel_calls == 0
    assert port.submit_calls == 0
    assert port.status_calls == 1


def test_missing_fingerprint_metadata_marks_result_incomplete() -> None:
    Policy, observe_job = _api()
    port = FakeJobPort(ProviderJobState.SUCCEEDED, {"measurements": ()})
    result = observe_job(
        _job(),
        job_port=port,
        policy=Policy(expected_measurements=()),
        metadata={"source_fingerprint": "sha256:source"},
    )

    assert result.status == "failed"
    assert "QPU_METADATA_INCOMPLETE" in result.diagnostic_codes


if __name__ == "__main__":
    tests = [
        test_successful_result_preserves_metadata_and_attempt_order,
        test_partial_result_is_failed_and_never_presented_as_success,
        test_failed_cancelled_timeout_and_unknown_states_are_distinct,
        test_cancel_is_explicit_and_polling_does_not_resubmit,
        test_missing_fingerprint_metadata_marks_result_incomplete,
    ]
    for test in tests:
        test()
    print("OK — LISS-0466 Red contract")
