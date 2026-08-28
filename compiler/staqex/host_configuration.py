"""Provider-neutral Host configuration preflight for live-capable paths."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class HostConfiguration:
    provider: str
    region: str
    device: str
    shots: int
    timeout_seconds: int
    cost_guard: int
    source_values: Mapping[str, object]


@dataclass(frozen=True)
class HostPreflightResult:
    status: str
    configuration: HostConfiguration
    precedence: tuple[str, ...]
    diagnostic_codes: tuple[str, ...]
    submit_allowed: bool
    submitter_called: bool
    network_called: bool
    secrets_redacted: bool
    audit_fields: dict[str, str]
    message: str


_PRECEDENCE = ("environment", "config_file", "defaults")
_DEFAULTS = {
    "provider": "aws-braket",
    "region": "",
    "device": "default-device",
    "shots": 100,
    "timeout_seconds": 300,
    "cost_guard": 10,
}
_CONFIG_KEYS = tuple(_DEFAULTS)


def _as_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _merge_layers(
    defaults: Mapping[str, object],
    config_file: Mapping[str, object],
    environment: Mapping[str, object],
) -> dict[str, object]:
    values = dict(_DEFAULTS)
    for layer in (defaults, config_file, environment):
        values.update({key: value for key, value in layer.items() if key in _CONFIG_KEYS})
    return values


def _configuration(values: Mapping[str, object]) -> HostConfiguration:
    return HostConfiguration(
        provider=str(values.get("provider", "")),
        region=str(values.get("region", "")),
        device=str(values.get("device", "")),
        shots=_as_int(values.get("shots"), 0),
        timeout_seconds=_as_int(values.get("timeout_seconds"), 0),
        cost_guard=_as_int(values.get("cost_guard"), 0),
        source_values=dict(values),
    )


def _conflicting_keys(
    defaults: Mapping[str, object], config_file: Mapping[str, object]
) -> tuple[str, ...]:
    return tuple(
        key
        for key in ("provider", "device")
        if key in defaults and key in config_file and defaults[key] != config_file[key]
    )


def _configuration_diagnostics(
    config: HostConfiguration,
    *,
    defaults: Mapping[str, object],
    config_file: Mapping[str, object],
    credential_state: Mapping[str, str],
) -> list[str]:
    diagnostics: list[str] = []
    if _conflicting_keys(defaults, config_file):
        diagnostics.append("CONFIG_CONFLICT")
    if not credential_state:
        diagnostics.append("CREDENTIAL_MISSING")
    if not config.device:
        diagnostics.append("DEVICE_CONFIG_INVALID")
    if config.shots <= 0:
        diagnostics.append("SHOTS_CONFIG_INVALID")
    if config.timeout_seconds <= 0:
        diagnostics.append("TIMEOUT_CONFIG_INVALID")
    if config.cost_guard <= 0:
        diagnostics.append("COST_GUARD_CONFIG_INVALID")
    return diagnostics


def _audit_fields(config: HostConfiguration, mode: str, credential_state: Mapping[str, str]) -> dict[str, str]:
    return {
        "provider": config.provider,
        "region": config.region,
        "mode": mode,
        "credential_state": "present" if credential_state else "missing",
    }


def preflight_host_configuration(
    *,
    configuration: HostConfiguration | None = None,
    defaults: Mapping[str, object] | None = None,
    config_file: Mapping[str, object] | None = None,
    environment: Mapping[str, object] | None = None,
    credential_state: Mapping[str, str] | None = None,
    mode: str = "preflight",
    submitter_called: bool = False,
) -> HostPreflightResult:
    """Validate Host inputs without reading secrets or performing I/O."""
    defaults = defaults or {}
    config_file = config_file or {}
    environment = environment or {}
    credential_state = credential_state or {}
    values = (
        dict(configuration.source_values)
        if configuration is not None
        else _merge_layers(defaults, config_file, environment)
    )
    config = configuration or _configuration(values)
    diagnostics = _configuration_diagnostics(
        config,
        defaults=defaults,
        config_file=config_file,
        credential_state=credential_state,
    )
    audit_fields = _audit_fields(config, mode, credential_state)
    if diagnostics:
        return HostPreflightResult(
            status="rejected",
            configuration=config,
            precedence=_PRECEDENCE,
            diagnostic_codes=tuple(dict.fromkeys(diagnostics)),
            submit_allowed=False,
            submitter_called=submitter_called,
            network_called=False,
            secrets_redacted=True,
            audit_fields=audit_fields,
            message="Host configuration rejected before provider submission.",
        )
    if mode in {"dry-run", "check"}:
        return HostPreflightResult(
            status=mode,
            configuration=config,
            precedence=_PRECEDENCE,
            diagnostic_codes=(),
            submit_allowed=False,
            submitter_called=False,
            network_called=False,
            secrets_redacted=True,
            audit_fields=audit_fields,
            message=f"Host configuration {mode} completed without submission.",
        )
    return HostPreflightResult(
        status="accepted",
        configuration=config,
        precedence=_PRECEDENCE,
        diagnostic_codes=(),
        submit_allowed=True,
        submitter_called=submitter_called,
        network_called=False,
        secrets_redacted=True,
        audit_fields=audit_fields,
        message="Host configuration preflight accepted.",
    )


__all__ = ["HostConfiguration", "HostPreflightResult", "preflight_host_configuration"]
