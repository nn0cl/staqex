"""Provider-neutral QPU job lifecycle and result-integrity boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from .qpu_submit import ProviderJobId, ProviderJobState


class JobPort(Protocol):
    def status(self, job_id: ProviderJobId) -> ProviderJobState:
        ...

    def result(self, job_id: ProviderJobId) -> Mapping[str, Any]:
        ...


@dataclass(frozen=True)
class JobLifecyclePolicy:
    expected_measurements: tuple[str, ...]


@dataclass(frozen=True)
class JobLifecycleResult:
    status: str
    measurements: tuple[Mapping[str, Any], ...] = ()
    metadata: dict[str, Any] | None = None
    diagnostic_codes: tuple[str, ...] = ()
    attempt: int | None = None


def _terminal_status(state: object, timeout_polls: int) -> tuple[str, tuple[str, ...]]:
    if state is ProviderJobState.FAILED:
        return "failed", ()
    if state is ProviderJobState.CANCELLED:
        return "cancelled", ()
    if state in (ProviderJobState.QUEUED, ProviderJobState.RUNNING):
        if timeout_polls > 0:
            return "timeout", ("QPU_JOB_TIMEOUT",)
        return "running", ()
    if state is ProviderJobState.SUCCEEDED:
        return "succeeded", ()
    return "failed", ("QPU_STATE_UNKNOWN",)


def _metadata_complete(metadata: Mapping[str, Any]) -> bool:
    required = ("source_fingerprint", "semantic_fingerprint", "artifact_fingerprint")
    return all(metadata.get(key) for key in required)


def _failed_result(
    metadata: Mapping[str, Any],
    code: str,
) -> JobLifecycleResult:
    attempt = metadata.get("attempt")
    return JobLifecycleResult(
        status="failed",
        metadata=dict(metadata),
        diagnostic_codes=(code,),
        attempt=attempt if isinstance(attempt, int) else None,
    )


def _attempt(metadata: Mapping[str, Any]) -> int | None:
    value = metadata.get("attempt")
    return value if isinstance(value, int) else None


def observe_job(
    job_id: ProviderJobId,
    *,
    job_port: JobPort,
    policy: JobLifecyclePolicy,
    metadata: Mapping[str, Any],
    timeout_polls: int = 0,
) -> JobLifecycleResult:
    """Observe one job once; this function never submits or retries it."""
    state = job_port.status(job_id)
    status, state_diagnostics = _terminal_status(state, timeout_polls)
    common_metadata = dict(metadata)
    if status != "succeeded":
        return JobLifecycleResult(
            status=status,
            metadata=common_metadata,
            diagnostic_codes=state_diagnostics,
            attempt=_attempt(common_metadata),
        )
    if not _metadata_complete(common_metadata):
        return _failed_result(common_metadata, "QPU_METADATA_INCOMPLETE")
    payload = job_port.result(job_id)
    values = payload.get("measurements", ())
    if not isinstance(values, (tuple, list)) or any(not isinstance(value, Mapping) for value in values):
        return _failed_result(common_metadata, "QPU_RESULT_INCOMPLETE")
    measurements = tuple(values)
    outputs = tuple(str(value.get("output", "")) for value in measurements)
    if outputs != policy.expected_measurements:
        return _failed_result(common_metadata, "QPU_RESULT_INCOMPLETE")
    return JobLifecycleResult(
        status="succeeded",
        measurements=measurements,
        metadata=common_metadata,
        attempt=_attempt(common_metadata),
    )


__all__ = ["JobLifecyclePolicy", "JobLifecycleResult", "observe_job"]
