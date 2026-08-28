"""Provider dependency policy checks without importing or installing an SDK."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DependencyPolicy:
    provider: str
    package: str
    minimum_safe_version: str
    adapter_module: str
    optional: bool
    imported_by: tuple[str, ...] = ()


@dataclass(frozen=True)
class DependencyInspection:
    status: str
    importable_without_dependency: bool
    provider_module: str
    sdk_imported: bool
    diagnostic_code: str
    submit_allowed: bool
    message: str
    boundary_ok: bool
    imported_by: tuple[str, ...]


def _version_parts(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split(".")[:3])


def _version_is_safe(installed: str, minimum: str) -> bool:
    return _version_parts(installed) >= _version_parts(minimum)


def _boundary_is_valid(policy: DependencyPolicy) -> bool:
    return policy.imported_by in ((), (policy.adapter_module,))


def _missing_dependency_message(policy: DependencyPolicy) -> str:
    return (
        f"{policy.package} is unavailable; install "
        f"{policy.package}>={policy.minimum_safe_version} for provider use."
    )


def _insecure_dependency_message(policy: DependencyPolicy, installed: str) -> str:
    return (
        f"{policy.package} {installed} is below the safe floor "
        f"{policy.minimum_safe_version}; CVE-2026-9291 remains applicable."
    )


def inspect_provider_dependency(
    policy: DependencyPolicy,
    *,
    installed_version: str | None,
) -> DependencyInspection:
    """Inspect package metadata only; never import the provider SDK."""
    boundary_ok = _boundary_is_valid(policy)
    if not boundary_ok:
        return DependencyInspection(
            status="rejected-boundary",
            importable_without_dependency=True,
            provider_module=policy.adapter_module,
            sdk_imported=False,
            diagnostic_code="PROVIDER_SDK_BOUNDARY_VIOLATION",
            submit_allowed=False,
            message="Provider SDK imports are allowed only in the Host adapter.",
            boundary_ok=False,
            imported_by=policy.imported_by,
        )
    if installed_version is None:
        return DependencyInspection(
            status="optional-missing" if policy.optional else "rejected-missing",
            importable_without_dependency=True,
            provider_module=policy.adapter_module,
            sdk_imported=False,
            diagnostic_code="PROVIDER_SDK_OPTIONAL_MISSING",
            submit_allowed=False,
            message=_missing_dependency_message(policy),
            boundary_ok=True,
            imported_by=policy.imported_by,
        )
    if not _version_is_safe(installed_version, policy.minimum_safe_version):
        return DependencyInspection(
            status="rejected-insecure",
            importable_without_dependency=True,
            provider_module=policy.adapter_module,
            sdk_imported=False,
            diagnostic_code="PROVIDER_SDK_INSECURE_VERSION",
            submit_allowed=False,
            message=_insecure_dependency_message(policy, installed_version),
            boundary_ok=True,
            imported_by=policy.imported_by,
        )
    return DependencyInspection(
        status="accepted",
        importable_without_dependency=True,
        provider_module=policy.adapter_module,
        sdk_imported=False,
        diagnostic_code="PROVIDER_SDK_POLICY_ACCEPTED",
        submit_allowed=True,
        message=f"{policy.package} {installed_version} satisfies the approved policy.",
        boundary_ok=True,
        imported_by=policy.imported_by,
    )


__all__ = ["DependencyInspection", "DependencyPolicy", "inspect_provider_dependency"]
