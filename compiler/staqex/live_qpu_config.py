"""Host-side non-secret configuration for live QPU submission."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import tomllib
from typing import Any, Mapping


class LiveQpuConfigError(ValueError):
    """Raised when the live-QPU configuration is unreadable or invalid."""


@dataclass(frozen=True)
class AwsBraketExecutionConfig:
    device_arn: str | None = None
    shots: int | None = None
    cost_ceiling_usd: float | None = None
    provider: str = "aws-braket"
    source_path: Path | None = None


def default_config_path() -> Path:
    configured = os.environ.get("STAQEX_QPU_CONFIG")
    if configured:
        return Path(configured).expanduser()
    config_home = os.environ.get("XDG_CONFIG_HOME")
    root = Path(config_home).expanduser() if config_home else Path.home() / ".config"
    return root / "staqex" / "qpu.toml"


def _positive_int(value: Any, field: str) -> int:
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise LiveQpuConfigError(f"{field} must be a positive integer") from exc
    if result <= 0:
        raise LiveQpuConfigError(f"{field} must be a positive integer")
    return result


def _positive_float(value: Any, field: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise LiveQpuConfigError(f"{field} must be a positive number") from exc
    if result <= 0:
        raise LiveQpuConfigError(f"{field} must be a positive number")
    return result


def load_aws_braket_config(path: str | Path | None = None) -> AwsBraketExecutionConfig:
    """Load non-secret AWS Braket settings from TOML when present."""
    config_path = Path(path).expanduser() if path is not None else default_config_path()
    if not config_path.exists():
        return AwsBraketExecutionConfig(source_path=None)
    try:
        with config_path.open("rb") as handle:
            document = tomllib.load(handle)
    except OSError as exc:
        raise LiveQpuConfigError(f"cannot read config file {config_path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise LiveQpuConfigError(f"invalid TOML in config file {config_path}: {exc}") from exc

    section = document.get("aws_braket", {})
    if not isinstance(section, Mapping):
        raise LiveQpuConfigError("[aws_braket] must be a TOML table")
    provider = str(section.get("provider", "aws-braket"))
    if provider != "aws-braket":
        raise LiveQpuConfigError(f"unsupported provider in config: {provider!r}")
    device = section.get("device_arn")
    device_arn = str(device).strip() if device is not None else None
    shots = _positive_int(section["shots"], "shots") if "shots" in section else None
    ceiling = (
        _positive_float(section["cost_ceiling_usd"], "cost_ceiling_usd")
        if "cost_ceiling_usd" in section
        else None
    )
    return AwsBraketExecutionConfig(
        device_arn=device_arn or None,
        shots=shots,
        cost_ceiling_usd=ceiling,
        provider=provider,
        source_path=config_path,
    )


__all__ = [
    "AwsBraketExecutionConfig",
    "LiveQpuConfigError",
    "default_config_path",
    "load_aws_braket_config",
]
