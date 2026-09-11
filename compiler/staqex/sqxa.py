"""Portable and target-resolved Staqex execution artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


class SqxaFormatError(ValueError):
    """Raised when an SQXA artifact is invalid or not executable."""


@dataclass(frozen=True)
class SqxaArtifact:
    source_identity: str
    semantic_identity: str
    execution_policy: Mapping[str, Any]
    provenance: Mapping[str, Any]
    payloads: Mapping[str, str]
    target: Mapping[str, Any] | None = None
    manifest: Mapping[str, Any] = field(default_factory=dict)

    @property
    def artifact_kind(self) -> str:
        return "targeted" if self.target is not None else "portable"


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _payload_hash(payload: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    return "sha256:" + digest


def _contains_secret(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(
            "secret" in str(key).lower()
            or "token" in str(key).lower()
            or "password" in str(key).lower()
            or "credential" in str(key).lower()
            or _contains_secret(item)
            for key, item in value.items()
        )
    if isinstance(value, (tuple, list)):
        return any(_contains_secret(item) for item in value)
    return False


def _payload(artifact: SqxaArtifact) -> dict[str, Any]:
    return {
        "source_identity": artifact.source_identity,
        "semantic_identity": artifact.semantic_identity,
        "execution_policy": dict(artifact.execution_policy),
        "provenance": dict(artifact.provenance),
        "payloads": dict(artifact.payloads),
        "target": dict(artifact.target) if artifact.target is not None else None,
    }


def _manifest(artifact: SqxaArtifact, payload: Mapping[str, Any]) -> dict[str, Any]:
    target = dict(artifact.target) if artifact.target is not None else None
    return {
        "format": "sqxa",
        "version": 1,
        "artifact_kind": artifact.artifact_kind,
        "source_identity": artifact.source_identity,
        "semantic_identity": artifact.semantic_identity,
        "provenance": dict(artifact.provenance),
        "execution_policy": dict(artifact.execution_policy),
        "target": target,
        "payload_hash": _payload_hash(payload),
    }


def _document(artifact: SqxaArtifact) -> dict[str, Any]:
    payload = _payload(artifact)
    return {"manifest": _manifest(artifact, payload), "payload": payload}


def write_sqxa(path: str | Path, artifact: SqxaArtifact) -> None:
    """Write a canonical SQXA document without secrets."""

    document = _document(artifact)
    if _contains_secret(document):
        raise SqxaFormatError("secret-bearing SQXA artifact is not allowed")
    Path(path).write_text(_canonical(document) + "\n", encoding="utf-8")


def _artifact_from_document(document: Mapping[str, Any]) -> SqxaArtifact:
    try:
        manifest = document["manifest"]
        payload = document["payload"]
        if not isinstance(manifest, Mapping) or not isinstance(payload, Mapping):
            raise TypeError("manifest and payload must be objects")
        if manifest.get("format") != "sqxa":
            raise SqxaFormatError("unsupported artifact format")
        expected_hash = _payload_hash(payload)
        if manifest.get("payload_hash") != expected_hash:
            raise SqxaFormatError("payload hash mismatch")
        if _contains_secret(document):
            raise SqxaFormatError("secret-bearing SQXA artifact is not allowed")
        return SqxaArtifact(
            source_identity=str(payload["source_identity"]),
            semantic_identity=str(payload["semantic_identity"]),
            execution_policy=dict(payload["execution_policy"]),
            provenance=dict(payload["provenance"]),
            payloads=dict(payload["payloads"]),
            target=(dict(payload["target"]) if payload.get("target") is not None else None),
            manifest=dict(manifest),
        )
    except (KeyError, TypeError, ValueError) as error:
        if isinstance(error, SqxaFormatError):
            raise
        raise SqxaFormatError("invalid SQXA document") from error


def load_sqxa(path: str | Path, *, expected_route: str | None = None) -> SqxaArtifact:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        artifact = _artifact_from_document(document)
    except (OSError, json.JSONDecodeError, TypeError) as error:
        raise SqxaFormatError("invalid SQXA document") from error
    _validate_route(artifact, expected_route)
    return artifact


def _validate_route(artifact: SqxaArtifact, expected_route: str | None) -> None:
    if expected_route is None:
        return
    route = artifact.target.get("route") if artifact.target else None
    if route != expected_route:
        raise SqxaFormatError("target route mismatch")


def build_target_variant(
    artifact: SqxaArtifact,
    *,
    route: str,
    device_id: str,
    capability_fingerprint: str,
    target_fingerprint: str,
    payload_format: str,
    capability_expires_at: str | None = None,
) -> SqxaArtifact:
    target = {
        "route": route,
        "device_id": device_id,
        "capability_fingerprint": capability_fingerprint,
        "target_fingerprint": target_fingerprint,
        "payload_format": payload_format,
    }
    if capability_expires_at is not None:
        target["capability_expires_at"] = capability_expires_at
    return SqxaArtifact(
        source_identity=artifact.source_identity,
        semantic_identity=artifact.semantic_identity,
        execution_policy=dict(artifact.execution_policy),
        provenance=dict(artifact.provenance),
        payloads=dict(artifact.payloads),
        target=target,
    )


class SqxaRuntime:
    """Validate targeted artifacts before constructing or calling a provider."""

    def __init__(self, *, provider: object | None = None, provider_factory: object | None = None):
        self._provider = provider
        self._provider_factory = provider_factory

    def prepare(
        self,
        path: str | Path,
        *,
        expected_route: str,
        now: datetime | None = None,
    ) -> SqxaArtifact:
        artifact = load_sqxa(path, expected_route=expected_route)
        if artifact.target is None:
            raise SqxaFormatError("target metadata is required")
        _validate_capability_expiry(artifact.target, now=now)
        if self._provider is None and self._provider_factory is not None:
            self._provider = self._provider_factory()
        return artifact


def _validate_capability_expiry(
    target: Mapping[str, Any], *, now: datetime | None
) -> None:
    expires_at = target.get("capability_expires_at")
    if expires_at is None:
        return
    expiry = datetime.fromisoformat(str(expires_at))
    current = now or datetime.now(timezone.utc)
    if current >= expiry:
        raise SqxaFormatError("capability expired")
