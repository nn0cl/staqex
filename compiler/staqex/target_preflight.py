"""Provider-neutral target capability preflight.

Profiles in this module are declarations used for offline target checks.  They
are not device observations and cannot authorize physical execution.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CapabilityProfile:
    profile_id: str
    profile_version: str
    provenance: dict[str, Any]
    calibration_status: str
    max_logical_qubits: int
    native_gates: tuple[str, ...]
    connectivity: tuple[tuple[int, int], ...]
    measurement_bases: tuple[str, ...]
    reset_supported: bool
    feed_forward_supported: bool
    max_shots: int
    max_depth: int
    timing_resolution_ns: int
    max_payload_bytes: int
    max_cost_units: int

    @property
    def physical_execution_claimed(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class ResourceDemand:
    logical_qubits: int
    gates: tuple[str, ...]
    connectivity: tuple[tuple[int, int], ...]
    measurement_bases: tuple[str, ...]
    needs_reset: bool
    needs_feed_forward: bool
    shots: int
    depth: int
    duration_ns: int
    payload_bytes: int
    cost_units: int


@dataclass(frozen=True, slots=True)
class PreflightDecision:
    status: str
    exceeded_dimensions: tuple[str, ...]
    profile_version: str
    provenance: dict[str, Any]
    physical_execution_claimed: bool
    allocation: None = None
    artifact: None = None
    provider_payload: None = None


def _append_if(exceeded: list[str], condition: bool, dimension: str) -> None:
    if condition:
        exceeded.append(dimension)


def _capability_exceeded(
    profile: CapabilityProfile, demand: ResourceDemand
) -> list[str]:
    exceeded: list[str] = []
    _append_if(
        exceeded,
        demand.logical_qubits > profile.max_logical_qubits,
        "logical_qubits",
    )
    _append_if(
        exceeded,
        any(gate not in profile.native_gates for gate in demand.gates),
        "native_gates",
    )
    supported_edges = set(profile.connectivity)
    _append_if(
        exceeded,
        any(edge not in supported_edges for edge in demand.connectivity),
        "connectivity",
    )
    _append_if(
        exceeded,
        any(
            basis not in profile.measurement_bases
            for basis in demand.measurement_bases
        ),
        "measurement_bases",
    )
    _append_if(
        exceeded,
        demand.needs_reset and not profile.reset_supported,
        "reset_supported",
    )
    _append_if(
        exceeded,
        demand.needs_feed_forward and not profile.feed_forward_supported,
        "feed_forward_supported",
    )
    return exceeded


def _resource_exceeded(
    profile: CapabilityProfile, demand: ResourceDemand
) -> list[str]:
    exceeded: list[str] = []
    _append_if(exceeded, demand.shots > profile.max_shots, "max_shots")
    _append_if(exceeded, demand.depth > profile.max_depth, "max_depth")
    _append_if(
        exceeded,
        demand.duration_ns > profile.timing_resolution_ns,
        "timing_resolution_ns",
    )
    _append_if(
        exceeded,
        demand.payload_bytes > profile.max_payload_bytes,
        "max_payload_bytes",
    )
    _append_if(
        exceeded,
        demand.cost_units > profile.max_cost_units,
        "max_cost_units",
    )
    return exceeded


def _exceeded_dimensions(
    profile: CapabilityProfile, demand: ResourceDemand
) -> tuple[str, ...]:
    exceeded = _capability_exceeded(profile, demand)
    exceeded.extend(_resource_exceeded(profile, demand))
    _append_if(
        exceeded,
        profile.calibration_status != "declared_only",
        "calibration_status",
    )
    return tuple(exceeded)


def preflight_target(
    profile: CapabilityProfile, demand: ResourceDemand
) -> PreflightDecision:
    """Evaluate declared target capacity without allocating or submitting."""

    exceeded = _exceeded_dimensions(profile, demand)
    return PreflightDecision(
        status="rejected" if exceeded else "supported",
        exceeded_dimensions=exceeded,
        profile_version=profile.profile_version,
        provenance=dict(profile.provenance),
        physical_execution_claimed=False,
    )
