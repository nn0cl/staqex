"""Provider-neutral lifecycle and capability contracts for Host execution.

This module deliberately contains no provider SDK, credentials, network call,
or provider-specific submission logic. Concrete adapters may translate their
raw responses into these small Host-owned records.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class NormalizedJobState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


class JobObservationState(str, Enum):
    OBSERVED = "observed"
    TIMED_OUT = "timed_out"
    UNREACHABLE = "unreachable"
    STALE = "stale"


@dataclass(frozen=True)
class JobObservation:
    provider_state: str
    normalized_state: NormalizedJobState
    observation_state: JobObservationState
    terminal: bool
    observed_at: datetime


@dataclass(frozen=True)
class CapabilityProfile:
    access_route: str
    hardware_provider: str
    device_id: str
    profile_fingerprint: str
    source: str
    availability: str
    captured_at: datetime
    expires_at: datetime
    calibration_reference: str | None = None
    freshness_policy: str = "explicit-expiry"
    capabilities: frozenset[str] = frozenset()


class CapabilityFreshnessError(ValueError):
    """Raised when a capability snapshot cannot authorize live preflight."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


_STATE_MAP = {
    "CREATED": NormalizedJobState.QUEUED,
    "QUEUED": NormalizedJobState.QUEUED,
    "WAITING": NormalizedJobState.QUEUED,
    "INITIALIZING": NormalizedJobState.QUEUED,
    "VALIDATING": NormalizedJobState.QUEUED,
    "RUNNING": NormalizedJobState.RUNNING,
    "EXECUTING": NormalizedJobState.RUNNING,
    "CANCELLING": NormalizedJobState.RUNNING,
    "COMPLETED": NormalizedJobState.SUCCEEDED,
    "SUCCEEDED": NormalizedJobState.SUCCEEDED,
    "DONE": NormalizedJobState.SUCCEEDED,
    "FAILED": NormalizedJobState.FAILED,
    "ERROR": NormalizedJobState.FAILED,
    "CANCELLED": NormalizedJobState.CANCELLED,
}
_TERMINAL_STATES = frozenset(
    {
        NormalizedJobState.SUCCEEDED,
        NormalizedJobState.FAILED,
        NormalizedJobState.CANCELLED,
    }
)


def _normalized_state(provider_state: str) -> NormalizedJobState:
    return _STATE_MAP.get(provider_state.upper(), NormalizedJobState.UNKNOWN)


def _is_terminal(
    normalized: NormalizedJobState,
    observation_state: JobObservationState,
) -> bool:
    return (
        observation_state is JobObservationState.OBSERVED
        and normalized in _TERMINAL_STATES
    )


def _identity_matches(
    profile: CapabilityProfile,
    *,
    expected_access_route: str | None,
    expected_hardware_provider: str | None,
    expected_device_id: str | None,
) -> bool:
    expected = (
        (expected_access_route, profile.access_route),
        (expected_hardware_provider, profile.hardware_provider),
        (expected_device_id, profile.device_id),
    )
    return all(
        expected_value is None or expected_value == actual
        for expected_value, actual in expected
    )


def map_provider_job_state(
    *,
    provider_state: str,
    observation_state: JobObservationState = JobObservationState.OBSERVED,
    observed_at: datetime | None = None,
) -> JobObservation:
    """Map a provider state without discarding the raw value."""

    normalized = _normalized_state(provider_state)
    terminal = _is_terminal(normalized, observation_state)
    return JobObservation(
        provider_state=provider_state,
        normalized_state=normalized,
        observation_state=observation_state,
        terminal=terminal,
        observed_at=observed_at or datetime.now(timezone.utc),
    )


def preflight_capability(
    profile: CapabilityProfile,
    *,
    now: datetime | None = None,
    expected_access_route: str | None = None,
    expected_hardware_provider: str | None = None,
    expected_device_id: str | None = None,
    required_capabilities: frozenset[str] = frozenset(),
) -> CapabilityProfile:
    """Validate a capability snapshot before a live submission."""

    current = now or datetime.now(timezone.utc)
    if not _identity_matches(
        profile,
        expected_access_route=expected_access_route,
        expected_hardware_provider=expected_hardware_provider,
        expected_device_id=expected_device_id,
    ):
        raise CapabilityFreshnessError("capability_identity_mismatch")
    if current >= profile.expires_at:
        raise CapabilityFreshnessError("capability_expired")
    if profile.availability != "online":
        raise CapabilityFreshnessError(f"capability_{profile.availability}")
    if not profile.profile_fingerprint:
        raise CapabilityFreshnessError("capability_identity_unverified")
    missing = required_capabilities - profile.capabilities
    if missing:
        raise CapabilityFreshnessError("capability_unsupported")
    return profile


__all__ = [
    "CapabilityFreshnessError",
    "CapabilityProfile",
    "JobObservation",
    "JobObservationState",
    "NormalizedJobState",
    "map_provider_job_state",
    "preflight_capability",
]
