"""Provider-neutral submit orchestration around an injected QPU port."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .qpu_submit import ProviderJobId, QpuSubmitRequest


class SubmitProvider(Protocol):
    def submit(self, request: QpuSubmitRequest) -> ProviderJobId:
        ...


@dataclass(frozen=True)
class SubmitIntegrationPolicy:
    max_qasm_bytes: int
    allowed_targets: tuple[str, ...]


@dataclass(frozen=True)
class SubmitIntegrationResult:
    status: str
    job_id: ProviderJobId | None
    diagnostic_codes: tuple[str, ...] = ()
    retryable: bool = False


def _cache_for(provider: SubmitProvider) -> dict[str, ProviderJobId]:
    cache = getattr(provider, "_staqex_idempotency", None)
    if cache is None:
        cache = {}
        setattr(provider, "_staqex_idempotency", cache)
    return cache


def _validate_request(
    request: QpuSubmitRequest, policy: SubmitIntegrationPolicy
) -> tuple[str, ...]:
    diagnostics: list[str] = []
    if len(request.artifact.qasm.encode("utf-8")) > policy.max_qasm_bytes:
        diagnostics.append("PAYLOAD_UNSUPPORTED")
    if request.artifact.target_profile not in policy.allowed_targets:
        diagnostics.append("TARGET_UNSUPPORTED")
    return tuple(diagnostics)


def _provider_failure(exc: Exception) -> SubmitIntegrationResult:
    if isinstance(exc, TimeoutError):
        return SubmitIntegrationResult("transient-failure", None, retryable=True)
    return SubmitIntegrationResult("permanent-failure", None)


def submit_artifact(
    request: QpuSubmitRequest,
    *,
    provider: SubmitProvider,
    policy: SubmitIntegrationPolicy,
    mode: str = "submit",
) -> SubmitIntegrationResult:
    """Validate and submit exactly once for each provider/idempotency key."""
    diagnostics = _validate_request(request, policy)
    if diagnostics:
        return SubmitIntegrationResult("rejected", None, diagnostics)
    if mode in {"dry-run", "check"}:
        return SubmitIntegrationResult(mode, None)

    cache = _cache_for(provider)
    existing = cache.get(request.idempotency_key)
    if existing is not None:
        return SubmitIntegrationResult("deduplicated", existing)
    try:
        job_id = provider.submit(request)
    except Exception as exc:
        return _provider_failure(exc)
    cache[request.idempotency_key] = job_id
    return SubmitIntegrationResult("submitted", job_id)


__all__ = [
    "SubmitIntegrationPolicy",
    "SubmitIntegrationResult",
    "submit_artifact",
]
