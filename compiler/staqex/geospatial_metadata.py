"""Provider-neutral X01 geospatial and sensor metadata profile.

This module stores descriptive mapping evidence only.  It does not decide road
passability, schedule sensor tasking, build Semantic IR, or project to a QPU.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType
from typing import Any


class GeospatialProfileError(ValueError):
    """An X01 record or relation violates the accepted profile contract."""


@dataclass(frozen=True)
class RawExtensionEvidence:
    """Hash-addressed evidence for an extension not interpreted by X01."""

    key: str
    value: Any
    sha256: str


@dataclass(frozen=True)
class MappingEvidence:
    """Source and profile identity retained for a mapped record."""

    source_id: str | None
    source_hash: str
    profile: str


@dataclass(frozen=True)
class GeospatialRecord:
    """Immutable view of one mapped X01 record."""

    id: str
    revision: int
    kind: str
    source_id: str | None
    source_hash: str
    profile: str
    geometry: Mapping[str, Any] | None
    crs: str | None
    crs_state: str
    lod: str | None
    foi_id: str | None
    property_id: str | None
    procedure_id: str | None
    phenomenon_time: str | None
    result_time: str | None
    ingest_time: str | None
    value: Any
    unit: str | None
    mapping_evidence: tuple[MappingEvidence, ...]
    extensions: Mapping[str, Any]


_PROFILE = "geosensor-x01-v1"
_CRS_PATTERN = re.compile(r"^EPSG:\d+$")
_GEOMETRY_TYPES = {"Point", "LineString", "Polygon"}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _validate_geometry(geometry: Any) -> Mapping[str, Any] | None:
    if geometry is None:
        return None
    if not isinstance(geometry, Mapping):
        raise GeospatialProfileError("geometry must be a mapping")
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")
    if geometry_type not in _GEOMETRY_TYPES:
        raise GeospatialProfileError("unsupported geometry type")
    if not isinstance(coordinates, list) or not coordinates:
        raise GeospatialProfileError("geometry coordinates are required")
    if geometry_type == "Point":
        _validate_position(coordinates)
    else:
        positions = coordinates[0] if geometry_type == "Polygon" else coordinates
        if not isinstance(positions, list) or len(positions) < 2:
            raise GeospatialProfileError("geometry needs at least two positions")
        for position in positions:
            _validate_position(position)
    return MappingProxyType(dict(geometry))


def _validate_position(position: Any) -> None:
    if (
        not isinstance(position, list)
        or len(position) < 2
        or any(
            not isinstance(value, (int, float)) or isinstance(value, bool)
            for value in position
        )
    ):
        raise GeospatialProfileError("geometry position is malformed")


def _record_key(record: Mapping[str, Any]) -> tuple[str, int]:
    identifier = record.get("id")
    revision = record.get("revision", 1)
    if not isinstance(identifier, str) or not identifier:
        raise GeospatialProfileError("record id is required")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise GeospatialProfileError("record revision must be positive")
    return identifier, revision


def _validate_crs(crs: Any) -> tuple[str | None, str]:
    if crs is not None and (
        not isinstance(crs, str) or not _CRS_PATTERN.fullmatch(crs)
    ):
        raise GeospatialProfileError("malformed CRS")
    return crs, "known" if crs is not None else "unknown"


def _validate_source_hash(source_hash: Any) -> str:
    if (
        not isinstance(source_hash, str)
        or len(source_hash) != 64
        or any(character not in "0123456789abcdef" for character in source_hash)
    ):
        raise GeospatialProfileError("source_hash must be a lowercase SHA-256 hex value")
    return source_hash


def _extension_evidence(
    identifier: str, extensions: Mapping[str, Any]
) -> dict[tuple[str, str], RawExtensionEvidence]:
    return {
        (identifier, key): RawExtensionEvidence(
            key=key,
            value=value,
            sha256=hashlib.sha256(_canonical(value).encode()).hexdigest(),
        )
        for key, value in extensions.items()
    }


def _mapped_record(record: Mapping[str, Any]) -> GeospatialRecord:
    identifier, revision = _record_key(record)
    kind = record.get("kind")
    if not isinstance(kind, str) or not kind:
        raise GeospatialProfileError("record kind is required")
    profile = record.get("profile", _PROFILE)
    if profile != _PROFILE:
        raise GeospatialProfileError("unsupported X01 profile")

    crs, crs_state = _validate_crs(record.get("crs"))
    extensions = record.get("extensions", {})
    if not isinstance(extensions, Mapping):
        raise GeospatialProfileError("extensions must be a mapping")
    source_id = record.get("source_id")
    if source_id is not None and not isinstance(source_id, str):
        raise GeospatialProfileError("source_id must be a string")
    source_hash = _validate_source_hash(record.get("source_hash"))
    geometry = _validate_geometry(record.get("geometry"))
    return GeospatialRecord(
        id=identifier,
        revision=revision,
        kind=kind,
        source_id=source_id,
        source_hash=source_hash,
        profile=profile,
        geometry=geometry,
        crs=crs,
        crs_state=crs_state,
        lod=record.get("lod"),
        foi_id=record.get("foi_id"),
        property_id=record.get("property_id"),
        procedure_id=record.get("procedure_id"),
        phenomenon_time=record.get("phenomenon_time"),
        result_time=record.get("result_time"),
        ingest_time=record.get("ingest_time"),
        value=record.get("value"),
        unit=record.get("unit"),
        mapping_evidence=(MappingEvidence(source_id, source_hash, profile),),
        extensions=MappingProxyType(dict(extensions)),
    )


class GeospatialMetadataProfile:
    """Immutable descriptive X01 profile with no execution authority."""

    is_executable = False

    def __init__(
        self,
        records: tuple[GeospatialRecord, ...],
        relations: tuple[tuple[str, str, str], ...],
        raw_extensions: Mapping[tuple[str, str], RawExtensionEvidence],
    ) -> None:
        self.records = records
        self.relations = relations
        self._by_id = {record.id: record for record in records}
        self._raw_extensions = raw_extensions

    @classmethod
    def from_records(
        cls,
        records: Iterable[Mapping[str, Any]],
        *,
        relations: Iterable[tuple[str, str, str]] = (),
    ) -> "GeospatialMetadataProfile":
        mapped: list[GeospatialRecord] = []
        seen: dict[tuple[str, int], str] = {}
        raw_extensions: dict[tuple[str, str], RawExtensionEvidence] = {}
        for source_record in records:
            if not isinstance(source_record, Mapping):
                raise GeospatialProfileError("record must be a mapping")
            content = _canonical(dict(source_record))
            key = _record_key(source_record)
            if key in seen:
                if seen[key] != content:
                    raise GeospatialProfileError("same id and revision has different content")
                continue
            mapped_record = _mapped_record(source_record)
            seen[key] = content
            mapped.append(mapped_record)
            extensions = source_record.get("extensions", {})
            raw_extensions.update(_extension_evidence(mapped_record.id, extensions))

        known_ids = {record.id for record in mapped}
        normalized_relations = tuple(tuple(relation) for relation in relations)
        for relation in normalized_relations:
            if len(relation) != 3:
                raise GeospatialProfileError(
                    "relation requires subject, predicate, object"
                )
            if relation[0] not in known_ids or relation[2] not in known_ids:
                raise GeospatialProfileError("relation endpoint does not exist")
        return cls(tuple(mapped), normalized_relations, MappingProxyType(raw_extensions))

    def record(self, identifier: str) -> GeospatialRecord:
        try:
            return self._by_id[identifier]
        except KeyError as error:
            raise GeospatialProfileError(f"unknown record: {identifier}") from error

    def raw_extension(self, identifier: str, key: str) -> RawExtensionEvidence:
        try:
            return self._raw_extensions[(identifier, key)]
        except KeyError as error:
            raise GeospatialProfileError(
                f"unknown extension: {identifier}/{key}"
            ) from error

    def domain_decision(self, _identifier: str, _decision: str) -> None:
        """Return no domain decision; geometry is not routing policy."""

        return None
