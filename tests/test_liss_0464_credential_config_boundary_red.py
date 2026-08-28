"""AT-TDD Phase 1 Red: LISS-0464 credential/configuration boundary."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _api():
    from compiler.staqex.host_configuration import (  # noqa: PLC0415
        HostConfiguration,
        preflight_host_configuration,
    )

    return HostConfiguration, preflight_host_configuration


def _config(**overrides):
    HostConfiguration, _ = _api()
    values = {
        "provider": "aws-braket",
        "region": "us-east-1",
        "device": "arn:aws:braket::device/fake",
        "shots": 100,
        "timeout_seconds": 300,
        "cost_guard": 10,
        "source_values": {},
    }
    values.update(overrides)
    return HostConfiguration(**values)


def test_precedence_is_deterministic_and_never_reads_secret_values() -> None:
    _, preflight = _api()
    result = preflight(
        defaults={"region": "default-region", "shots": 10},
        config_file={"region": "file-region", "shots": 50},
        environment={"region": "env-region", "shots": "100"},
        credential_state={"AWS_ACCESS_KEY_ID": "present"},
    )

    assert result.status == "accepted"
    assert result.configuration.region == "env-region"
    assert result.configuration.shots == 100
    assert result.precedence == ("environment", "config_file", "defaults")
    assert result.secrets_redacted is True
    assert result.audit_fields["credential_state"] == "present"


def test_missing_or_invalid_configuration_rejects_before_submit() -> None:
    _, preflight = _api()
    result = preflight(
        configuration=_config(device=""),
        credential_state={},
        submitter_called=False,
    )

    assert result.status == "rejected"
    assert "CREDENTIAL_MISSING" in result.diagnostic_codes
    assert "DEVICE_CONFIG_INVALID" in result.diagnostic_codes
    assert result.submit_allowed is False
    assert result.submitter_called is False


def test_invalid_shots_timeout_and_cost_guard_fail_before_network_work() -> None:
    _, preflight = _api()
    result = preflight(
        configuration=_config(shots=0, timeout_seconds=-1, cost_guard=0),
        credential_state={"AWS_ACCESS_KEY_ID": "present"},
        submitter_called=False,
    )

    assert result.status == "rejected"
    assert {
        "SHOTS_CONFIG_INVALID",
        "TIMEOUT_CONFIG_INVALID",
        "COST_GUARD_CONFIG_INVALID",
    } <= set(result.diagnostic_codes)
    assert result.network_called is False
    assert result.submit_allowed is False


def test_dry_run_and_check_never_submit_and_audit_contains_no_secret() -> None:
    _, preflight = _api()
    result = preflight(
        configuration=_config(),
        credential_state={"AWS_ACCESS_KEY_ID": "present"},
        mode="dry-run",
        submitter_called=False,
    )

    assert result.status == "dry-run"
    assert result.submit_allowed is False
    assert result.submitter_called is False
    assert result.network_called is False
    assert result.audit_fields["mode"] == "dry-run"
    assert all("secret" not in str(value).lower() for value in result.audit_fields.values())


def test_conflicting_provider_or_device_sources_reject_without_exposing_values() -> None:
    _, preflight = _api()
    result = preflight(
        defaults={"provider": "aws-braket", "device": "device-a"},
        config_file={"provider": "other-provider", "device": "device-b"},
        environment={},
        credential_state={"AWS_ACCESS_KEY_ID": "present"},
    )

    assert result.status == "rejected"
    assert "CONFIG_CONFLICT" in result.diagnostic_codes
    assert result.submit_allowed is False
    assert "device-a" not in result.message
    assert "device-b" not in result.message


if __name__ == "__main__":
    tests = [
        test_precedence_is_deterministic_and_never_reads_secret_values,
        test_missing_or_invalid_configuration_rejects_before_submit,
        test_invalid_shots_timeout_and_cost_guard_fail_before_network_work,
        test_dry_run_and_check_never_submit_and_audit_contains_no_secret,
        test_conflicting_provider_or_device_sources_reject_without_exposing_values,
    ]
    for test in tests:
        test()
    print("OK — LISS-0464 Red contract")
