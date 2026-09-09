"""Provider-neutral SQXA artifact persistence and runtime loading."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class SqxaArtifact:
    schema_version: str
    artifact_id: str
    problem_id: str
    variables: tuple[str, ...]
    qubo_terms: tuple[tuple[str, str, float], ...]
    offset: float
    encoding: Mapping[str, Any]
    runtime: Mapping[str, Any]
    source_hash: str


@dataclass(frozen=True)
class RuntimeInput:
    status: str
    artifact: SqxaArtifact
    runtime_kind: str
    capability: str


class SqxaValidationError(ValueError):
    """Raised when an SQXA artifact cannot be trusted or understood."""


class RuntimeLoadError(ValueError):
    """Raised when an artifact cannot be loaded by the local runtime lane."""


_SUPPORTED_SCHEMA = "sqxa/1"
_SUPPORTED_RUNTIME = "local-simulator"


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _content_hash(payload: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()
    return "sha256:" + digest


def _payload(artifact: SqxaArtifact) -> dict[str, Any]:
    return asdict(artifact)


def _document(artifact: SqxaArtifact) -> dict[str, Any]:
    payload = _payload(artifact)
    return {"payload": payload, "content_hash": _content_hash(payload)}


def _validate_schema(schema_version: Any) -> None:
    if schema_version != _SUPPORTED_SCHEMA:
        raise SqxaValidationError(f"unsupported schema: {schema_version}")


def write_sqxa(artifact: SqxaArtifact, path: str | Path) -> None:
    """Write one self-contained, content-addressed SQXA artifact."""

    _validate_schema(artifact.schema_version)
    Path(path).write_text(
        _canonical_json(_document(artifact)) + "\n",
        encoding="utf-8",
    )


def _restore_encoding(payload: Mapping[str, Any]) -> dict[str, Any]:
    encoding = dict(payload["encoding"])
    if isinstance(encoding.get("bit_order"), list):
        encoding["bit_order"] = tuple(encoding["bit_order"])
    return encoding


def _artifact_from_payload(payload: Mapping[str, Any]) -> SqxaArtifact:
    try:
        return SqxaArtifact(
            schema_version=str(payload["schema_version"]),
            artifact_id=str(payload["artifact_id"]),
            problem_id=str(payload["problem_id"]),
            variables=tuple(str(value) for value in payload["variables"]),
            qubo_terms=tuple(
                (str(left), str(right), float(coefficient))
                for left, right, coefficient in payload["qubo_terms"]
            ),
            offset=float(payload["offset"]),
            encoding=_restore_encoding(payload),
            runtime=dict(payload["runtime"]),
            source_hash=str(payload["source_hash"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise SqxaValidationError("invalid SQXA payload") from error


def _read_document(path: str | Path) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
        payload = document["payload"]
        if not isinstance(document, Mapping) or not isinstance(payload, Mapping):
            raise TypeError("SQXA document and payload must be objects")
        return document, payload
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise SqxaValidationError("invalid SQXA document") from error


def read_sqxa(path: str | Path) -> SqxaArtifact:
    """Read and validate an SQXA artifact before exposing its payload."""

    document, payload = _read_document(path)
    _validate_schema(payload.get("schema_version"))
    if document.get("content_hash") != _content_hash(payload):
        raise SqxaValidationError("content hash mismatch")
    return _artifact_from_payload(payload)


def _runtime_capability(runtime_kind: Any) -> str:
    if runtime_kind != _SUPPORTED_RUNTIME:
        raise RuntimeLoadError(f"unsupported runtime: {runtime_kind}")
    return "finite-binary-projection"


def load_runtime(path: str | Path) -> RuntimeInput:
    """Load only artifacts supported by the provider-neutral local lane."""

    artifact = read_sqxa(path)
    runtime_kind = artifact.runtime.get("kind")
    capability = _runtime_capability(runtime_kind)
    return RuntimeInput(
        status="ready",
        artifact=artifact,
        runtime_kind=_SUPPORTED_RUNTIME,
        capability=capability,
    )
