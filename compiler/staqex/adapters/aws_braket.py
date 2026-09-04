"""AWS Braket Host adapter (ADR 0202, LISS-0392).

Implements the provider-neutral `QpuSubmitPort` / `QpuJobPort`
(`compiler/staqex/qpu_submit.py`) against AWS Braket. This module is a
Host adapter, never imported by Kernel code, and never imported by this
adapter's own test suite in its real (non-fake) form.

Standing safety constraints (ADR 0202 Decisions 3 and 5, restated here
because they govern this file's behavior, not just its design record):

- Credentials flow only through the existing `CredentialPort`
  (`compiler/staqex/credentials.py`) -- never hardcoded, never logged.
- `RealAwsBraketClient` lazy-imports `amazon-braket-sdk` only when
  actually instantiated, and refuses to construct at all unless the
  installed version is >= 1.117.0 -- CVE-2026-9291 (CVSS 7.1) is an
  insecure-deserialization vulnerability in exactly the job-result-
  processing path this adapter's `QpuJobPort.result` wraps, fixed in
  1.117.0. This check runs against installed package metadata only
  (`importlib.metadata.version`), not a heavy import, so it is cheap and
  fails closed before any SDK code executes.
- Building and testing this adapter is code authorship against an
  injected fake client. It does not, by itself, submit anything real.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from ..credentials import CredentialPort
from ..qpu_submit import ProviderJobId, ProviderJobState, QpuSubmitRequest

_MIN_SAFE_BRAKET_SDK_VERSION = "1.117.0"
_CVE_ID = "CVE-2026-9291"


class BraketClientPort(Protocol):
    """Minimal client surface this adapter needs -- not a full SDK re-export."""

    def create_task(self, qasm: str, device_arn: str, shots: int) -> str:
        """Submit a QASM3 circuit; return a provider task ARN."""
        ...

    def task_state(self, task_arn: str) -> str:
        ...

    def task_result(self, task_arn: str) -> Mapping[str, Any]:
        ...

    def cancel_task(self, task_arn: str) -> None:
        ...


class BraketCredentialError(Exception):
    """Raised when required AWS credentials are missing (fail closed)."""


class BraketDependencyError(Exception):
    """Raised when amazon-braket-sdk is absent or below the CVE-fixed version."""


def _installed_braket_sdk_version() -> str | None:
    """Return the installed amazon-braket-sdk version, or None if absent.

    Uses package metadata only -- does not import the SDK's own modules.
    Module-level so tests can monkeypatch it without a real install.
    """
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version("amazon-braket-sdk")
    except PackageNotFoundError:
        return None


def _version_at_least(installed: str, minimum: str) -> bool:
    installed_parts = [int(p) for p in installed.split(".")[:3]]
    minimum_parts = [int(p) for p in minimum.split(".")[:3]]
    return installed_parts >= minimum_parts


class RealAwsBraketClient:
    """Thin wrapper over the real amazon-braket-sdk, version-gated.

    Never imported or instantiated by this Issue's own test suite -- the
    real SDK import happens only if a caller actually constructs this
    class in an environment with the package installed.
    """

    def __init__(self) -> None:
        installed = _installed_braket_sdk_version()
        if installed is None:
            raise BraketDependencyError(
                "amazon-braket-sdk is not installed. Install "
                f"amazon-braket-sdk>={_MIN_SAFE_BRAKET_SDK_VERSION} to use "
                "the real AWS Braket adapter."
            )
        if not _version_at_least(installed, _MIN_SAFE_BRAKET_SDK_VERSION):
            raise BraketDependencyError(
                f"amazon-braket-sdk {installed} is vulnerable to {_CVE_ID} "
                "(CVSS 7.1, insecure deserialization in job result "
                f"processing). Upgrade to >={_MIN_SAFE_BRAKET_SDK_VERSION}."
            )
        # Lazy import: only reached once the version check above passes.
        from braket.aws import AwsDevice, AwsQuantumTask  # type: ignore[import-not-found]

        self._AwsDevice = AwsDevice
        self._AwsQuantumTask = AwsQuantumTask

    def create_task(self, qasm: str, device_arn: str, shots: int) -> str:
        try:
            device = self._AwsDevice(device_arn)
            task = device.run(qasm, shots=shots)
        except Exception as exc:
            if exc.__class__.__name__ in {
                "NoCredentialsError",
                "PartialCredentialsError",
                "ProfileNotFound",
            }:
                raise BraketCredentialError(
                    "AWS Braket submit refused: the AWS SDK could not resolve "
                    "credentials from its standard credential chain"
                ) from exc
            raise
        return str(task.id)

    def task_state(self, task_arn: str) -> str:
        return str(self._AwsQuantumTask(arn=task_arn).state())

    def task_result(self, task_arn: str) -> Mapping[str, Any]:
        result = self._AwsQuantumTask(arn=task_arn).result()
        measurements = result.measurements
        if hasattr(measurements, "tolist"):
            measurements = measurements.tolist()
        return {"measurements": measurements, "task_arn": task_arn}

    def cancel_task(self, task_arn: str) -> None:
        self._AwsQuantumTask(arn=task_arn).cancel()


_STATE_MAP = {
    "CREATED": ProviderJobState.QUEUED,
    "QUEUED": ProviderJobState.QUEUED,
    "RUNNING": ProviderJobState.RUNNING,
    "COMPLETED": ProviderJobState.SUCCEEDED,
    "FAILED": ProviderJobState.FAILED,
    "CANCELLED": ProviderJobState.CANCELLED,
}


@dataclass
class AwsBraketAdapter:
    """QpuSubmitPort / QpuJobPort backed by AWS Braket.

    `client` is injected (Dependency Inversion) -- production callers
    pass a `RealAwsBraketClient()`; tests pass a fake implementing
    `BraketClientPort`. This class never imports amazon-braket-sdk
    itself.
    """

    client: BraketClientPort
    device_arn: str
    credentials: CredentialPort
    required_credentials: tuple[str, ...] = ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY")
    default_shots: int = 100

    def _require_credentials(self) -> None:
        # Accept either explicit environment credentials or a configured
        # standard-chain source. The SDK then resolves the actual secret
        # (including SSO/profile files) without this adapter reading or
        # logging it.
        if all(self.credentials.get(name) is not None for name in self.required_credentials):
            return
        chain_sources = (
            "AWS_PROFILE",
            "AWS_WEB_IDENTITY_TOKEN_FILE",
            "AWS_CONTAINER_CREDENTIALS_RELATIVE_URI",
            "AWS_CONTAINER_CREDENTIALS_FULL_URI",
        )
        if any(self.credentials.get(name) is not None for name in chain_sources):
            return
        missing = tuple(
            name for name in self.required_credentials if self.credentials.get(name) is None
        )
        if missing:
            raise BraketCredentialError(
                "AWS Braket submit refused: missing Host credentials "
                + ", ".join(missing)
            )

    def submit(self, request: QpuSubmitRequest) -> ProviderJobId:
        self._require_credentials()
        shots = int(request.execution_settings.get("shots", self.default_shots))
        task_arn = self.client.create_task(request.artifact.qasm, self.device_arn, shots)
        return ProviderJobId(provider="aws-braket", opaque_id=task_arn)

    def status(self, job_id: ProviderJobId) -> ProviderJobState:
        raw = self.client.task_state(job_id.opaque_id)
        return _STATE_MAP.get(raw, ProviderJobState.RUNNING)

    def wait(self, job_id: ProviderJobId) -> ProviderJobState:
        return self.status(job_id)

    def result(self, job_id: ProviderJobId) -> Mapping[str, Any]:
        return self.client.task_result(job_id.opaque_id)

    def cancel(self, job_id: ProviderJobId) -> ProviderJobState:
        self.client.cancel_task(job_id.opaque_id)
        return self.status(job_id)


__all__ = [
    "AwsBraketAdapter",
    "BraketClientPort",
    "BraketCredentialError",
    "BraketDependencyError",
    "RealAwsBraketClient",
]
