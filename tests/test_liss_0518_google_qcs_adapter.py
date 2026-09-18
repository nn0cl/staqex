"""Offline Google QCS capability-profile contract."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from compiler.staqex.adapters.google_qcs import GoogleQcsAdapter


class FakeGoogleQcsClient:
    """Deterministic fake; it never imports Cirq or contacts Google Cloud."""

    def capability_snapshot(
        self, project_id: str, processor_id: str
    ) -> dict[str, Any]:
        return {
            "hardware_provider": "google",
            "provider_device_id": processor_id,
            "capabilities": ("openqasm3", "measure"),
            "availability": "online",
            "captured_at": datetime.now(timezone.utc),
        }


def test_google_adapter_import_is_sdk_independent() -> None:
    """The Host adapter module must load without Google SDK installation."""

    assert GoogleQcsAdapter is not None


def test_capability_profile_separates_route_and_device_identity() -> None:
    adapter = GoogleQcsAdapter(
        client=FakeGoogleQcsClient(),
        project_id="fake-project",
        processor_id="fake-processor",
    )

    profile = adapter.capability_profile()

    assert profile.access_route == "google-qcs"
    assert profile.hardware_provider == "google"
    assert profile.device_id == "fake-processor"
    assert profile.availability == "online"
    assert profile.capabilities == frozenset({"measure", "openqasm3"})
