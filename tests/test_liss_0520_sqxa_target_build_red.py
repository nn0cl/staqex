"""AT-TDD Phase 1 Red: one `.sqxa` format with portable/targeted variants."""

from __future__ import annotations

import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterator, Type

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from compiler.staqex.sqxa import (  # type: ignore[import-not-found]
    SqxaArtifact,
    SqxaFormatError,
    SqxaRuntime,
    build_target_variant,
    load_sqxa,
    write_sqxa,
)


@contextmanager
def raises(expected: Type[BaseException], match: str = "") -> Iterator[None]:
    try:
        yield
    except expected as exc:
        if match and match not in str(exc):
            raise AssertionError(f"{match!r} not found in {exc!r}") from exc
    else:
        raise AssertionError(f"expected {expected.__name__}")


def _portable() -> SqxaArtifact:
    return SqxaArtifact(
        source_identity="sha256:source",
        semantic_identity="sha256:semantic",
        execution_policy={"shots": 100},
        provenance={"source_id": "bell.sqx"},
        payloads={"openqasm3": "OPENQASM 3.0;\n"},
    )


def test_portable_sqxa_round_trip_preserves_common_identity(tmp_path: Path) -> None:
    path = tmp_path / "bell.sqxa"

    write_sqxa(path, _portable())
    loaded = load_sqxa(path)

    assert loaded.manifest["format"] == "sqxa"
    assert loaded.manifest["artifact_kind"] == "portable"
    assert loaded.source_identity == "sha256:source"
    assert loaded.semantic_identity == "sha256:semantic"
    assert loaded.payloads["openqasm3"] == "OPENQASM 3.0;\n"


def test_target_build_keeps_sqxa_extension_and_adds_target_variant(
    tmp_path: Path,
) -> None:
    source = tmp_path / "bell.sqxa"
    target = tmp_path / "bell.aws-braket.sqxa"
    write_sqxa(source, _portable())

    targeted = build_target_variant(
        _portable(),
        route="aws-braket",
        device_id="arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
        capability_fingerprint="sha256:capability",
        target_fingerprint="sha256:target",
        payload_format="openqasm3",
    )
    write_sqxa(target, targeted)
    loaded = load_sqxa(target)

    assert target.suffix == ".sqxa"
    assert loaded.manifest["artifact_kind"] == "targeted"
    assert loaded.manifest["target"]["route"] == "aws-braket"
    assert loaded.manifest["target"]["device_id"].endswith("Aria-1")
    assert loaded.manifest["target"]["capability_fingerprint"] == "sha256:capability"
    assert loaded.manifest["target"]["payload_format"] == "openqasm3"
    assert loaded.manifest["target"]["target_fingerprint"] == "sha256:target"
    assert loaded.source_identity == "sha256:source"
    assert loaded.semantic_identity == "sha256:semantic"


def test_runtime_rejects_target_mismatch_before_provider_access(
    tmp_path: Path,
) -> None:
    path = tmp_path / "bell.aws-braket.sqxa"
    write_sqxa(
        path,
        build_target_variant(
            _portable(),
            route="aws-braket",
            device_id="arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
            capability_fingerprint="sha256:capability",
            target_fingerprint="sha256:target",
            payload_format="openqasm3",
        ),
    )

    with raises(SqxaFormatError, match="target"):
        load_sqxa(path, expected_route="azure-quantum")


def test_runtime_rejects_expired_capability_before_provider_access(
    tmp_path: Path,
) -> None:
    path = tmp_path / "expired.aws-braket.sqxa"
    write_sqxa(
        path,
        build_target_variant(
            _portable(),
            route="aws-braket",
            device_id="arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
            capability_fingerprint="sha256:expired",
            target_fingerprint="sha256:target",
            payload_format="openqasm3",
            capability_expires_at="2026-09-01T00:00:00+00:00",
        ),
    )

    class FakeProvider:
        calls = 0

        def submit(self, _artifact: object) -> None:
            self.calls += 1

    runtime = SqxaRuntime(provider_factory=FakeProvider)
    with raises(SqxaFormatError, match="expired"):
        runtime.prepare(
            path,
            expected_route="aws-braket",
            now=datetime(2026, 9, 10, tzinfo=timezone.utc),
        )
    assert provider.calls == 0


def test_runtime_target_mismatch_does_not_construct_or_call_provider(
    tmp_path: Path,
) -> None:
    path = tmp_path / "bell.aws-braket.sqxa"
    write_sqxa(
        path,
        build_target_variant(
            _portable(),
            route="aws-braket",
            device_id="arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1",
            capability_fingerprint="sha256:capability",
            target_fingerprint="sha256:target",
            payload_format="openqasm3",
        ),
    )

    class FakeProvider:
        constructions = 0

        def __init__(self) -> None:
            self.constructions += 1

    provider = FakeProvider()
    runtime = SqxaRuntime(provider=provider)
    with raises(SqxaFormatError, match="target"):
        runtime.prepare(path, expected_route="azure-quantum")
    assert FakeProvider.constructions == 0


def test_sqxa_rejects_secret_bearing_manifest_or_payload(tmp_path: Path) -> None:
    path = tmp_path / "secret.sqxa"
    artifact = SqxaArtifact(
        source_identity="sha256:source",
        semantic_identity="sha256:semantic",
        execution_policy={},
        provenance={},
        payloads={"aws_secret_access_key": "must-not-be-stored"},
    )

    with raises(SqxaFormatError, match="secret"):
        write_sqxa(path, artifact)


def _run() -> int:
    tests = [
        test_portable_sqxa_round_trip_preserves_common_identity,
        test_target_build_keeps_sqxa_extension_and_adds_target_variant,
        test_runtime_rejects_target_mismatch_before_provider_access,
        test_runtime_rejects_expired_capability_before_provider_access,
        test_runtime_target_mismatch_does_not_construct_or_call_provider,
        test_sqxa_rejects_secret_bearing_manifest_or_payload,
    ]
    failures: list[str] = []
    for test in tests:
        with TemporaryDirectory(prefix="liss-0520-") as temp_dir:
            try:
                test(Path(temp_dir))
            except Exception as exc:  # noqa: BLE001 - aggregate all Red failures
                failures.append(f"{test.__name__}: {exc}")
    if failures:
        print("Phase 1 Red — expected failures:")
        print("\n".join(failures))
        return 1
    print("UNEXPECTED: LISS-0520 Red tests passed")
    return 1


if __name__ == "__main__":
    raise SystemExit(_run())
