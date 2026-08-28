"""AT-TDD Phase 1 Red: LISS-0463 provider dependency isolation."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _api():
    from compiler.staqex.provider_dependency_policy import (  # noqa: PLC0415
        DependencyPolicy,
        inspect_provider_dependency,
    )

    return DependencyPolicy, inspect_provider_dependency


def _policy(**overrides):
    DependencyPolicy, _ = _api()
    values = {
        "provider": "aws-braket",
        "package": "amazon-braket-sdk",
        "minimum_safe_version": "1.117.0",
        "adapter_module": "compiler.staqex.adapters.aws_braket",
        "optional": True,
    }
    values.update(overrides)
    return DependencyPolicy(**values)


def test_local_policy_is_provider_optional_and_kernel_never_imports_sdk() -> None:
    _, inspect_provider_dependency = _api()
    result = inspect_provider_dependency(_policy(), installed_version=None)

    assert result.status == "optional-missing"
    assert result.importable_without_dependency is True
    assert result.provider_module == "compiler.staqex.adapters.aws_braket"
    assert result.sdk_imported is False
    assert result.diagnostic_code == "PROVIDER_SDK_OPTIONAL_MISSING"


def test_missing_sdk_failure_is_actionable_and_fail_closed() -> None:
    _, inspect_provider_dependency = _api()
    result = inspect_provider_dependency(_policy(), installed_version=None)

    assert result.submit_allowed is False
    assert "amazon-braket-sdk" in result.message
    assert "1.117.0" in result.message
    assert result.sdk_imported is False


def test_below_fixed_security_version_is_rejected_without_import() -> None:
    _, inspect_provider_dependency = _api()
    result = inspect_provider_dependency(_policy(), installed_version="1.116.9")

    assert result.status == "rejected-insecure"
    assert result.submit_allowed is False
    assert result.diagnostic_code == "PROVIDER_SDK_INSECURE_VERSION"
    assert "CVE-2026-9291" in result.message
    assert result.sdk_imported is False


def test_dependency_policy_rejects_provider_sdk_imports_outside_host_adapter() -> None:
    _, inspect_provider_dependency = _api()
    result = inspect_provider_dependency(
        _policy(imported_by=("compiler.staqex.adapters.aws_braket",)),
        installed_version="1.117.0",
    )

    assert result.status == "accepted"
    assert result.boundary_ok is True
    assert result.imported_by == ("compiler.staqex.adapters.aws_braket",)


if __name__ == "__main__":
    tests = [
        test_local_policy_is_provider_optional_and_kernel_never_imports_sdk,
        test_missing_sdk_failure_is_actionable_and_fail_closed,
        test_below_fixed_security_version_is_rejected_without_import,
        test_dependency_policy_rejects_provider_sdk_imports_outside_host_adapter,
    ]
    for test in tests:
        test()
    print("OK — LISS-0463 Red contract")
