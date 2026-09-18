"""Offline-safe Google QCS Host adapter boundary.

This module owns only the provider access boundary.  Google SDK imports and
credentials remain optional Host concerns and are deliberately absent from
the module-level import path so local compilation and fake-client tests work
without Google dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Mapping, Protocol

from ..qpu_contract import CapabilityProfile


class GoogleQcsClientPort(Protocol):
    """Minimal injected surface for offline capability-profile tests."""

    def capability_snapshot(
        self, project_id: str, processor_id: str
    ) -> Mapping[str, Any]:
        """Return a provider capability snapshot without changing semantics."""


@dataclass(frozen=True)
class GoogleQcsAdapter:
    """Provider-neutral capability boundary for Google QCS.

    The client is injected so this adapter remains deterministic and
    dependency-free in local tests.  A future SDK-backed client belongs in
    this Host adapter boundary and must not be imported by the Kernel.
    """

    client: GoogleQcsClientPort
    project_id: str
    processor_id: str
    capability_ttl: timedelta = timedelta(minutes=5)

    def capability_profile(self) -> CapabilityProfile:
        """Translate one Google capability snapshot into the Host contract."""

        snapshot = self.client.capability_snapshot(
            self.project_id,
            self.processor_id,
        )
        provider = str(snapshot.get("hardware_provider", "google")).lower()
        device_id = str(snapshot.get("provider_device_id", self.processor_id))
        captured_at = snapshot.get("captured_at")
        if not isinstance(captured_at, datetime):
            captured_at = datetime.now(timezone.utc)
        elif captured_at.tzinfo is None:
            captured_at = captured_at.replace(tzinfo=timezone.utc)
        capabilities = frozenset(str(item) for item in snapshot.get("capabilities", ()))
        fingerprint_input = "|".join(
            (self.project_id, self.processor_id, provider, device_id, *sorted(capabilities))
        ).encode("utf-8")
        return CapabilityProfile(
            access_route="google-qcs",
            hardware_provider=provider,
            device_id=device_id,
            profile_fingerprint=hashlib.sha256(fingerprint_input).hexdigest(),
            source="google-qcs-capability-snapshot",
            availability=str(snapshot.get("availability", "unknown")).lower(),
            captured_at=captured_at,
            expires_at=captured_at + self.capability_ttl,
            calibration_reference=(
                str(snapshot["calibration_reference"])
                if snapshot.get("calibration_reference") is not None
                else None
            ),
            capabilities=capabilities,
        )


__all__ = ["GoogleQcsAdapter", "GoogleQcsClientPort"]
