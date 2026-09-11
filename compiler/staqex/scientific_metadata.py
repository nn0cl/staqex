"""Descriptive scientific metadata graph for the M0 workflow contract.

The graph stores identity, observational classification, evidence, and
provenance.  It deliberately has no execution, Semantic IR, or QPU
projection authority.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
import json
from typing import Any


class GraphValidationError(ValueError):
    """A metadata identity, reference, or dimension contract is invalid."""


class ImmutableSnapshotError(TypeError):
    """A caller attempted to mutate an immutable graph snapshot."""


class ProvenanceCycleError(GraphValidationError):
    """A derivation relation contains a cycle."""


class _ImmutableRecord(dict[str, Any]):
    """Mapping with a domain-specific error for snapshot mutation attempts."""

    def _immutable(self, *args: Any, **kwargs: Any) -> None:
        raise ImmutableSnapshotError("metadata snapshots are immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable


_UNIT_DIMENSIONS = {
    "m": "Length",
    "cm": "Length",
    "mm": "Length",
    "s": "Time",
    "ms": "Time",
    "rad": "Angle",
    "deg": "Angle",
}


def _record_key(record: Mapping[str, Any]) -> tuple[str, int]:
    identifier = record.get("id")
    if not isinstance(identifier, str) or not identifier.strip():
        raise GraphValidationError("metadata record requires a non-empty id")
    revision = record.get("revision", 1)
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise GraphValidationError("metadata revision must be a positive integer")
    return identifier, revision


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _normalize_records(
    records: Iterable[Mapping[str, Any]],
) -> tuple[_ImmutableRecord, ...]:
    normalized: list[_ImmutableRecord] = []
    seen: dict[tuple[str, int], str] = {}
    for source_record in records:
        if not isinstance(source_record, Mapping):
            raise GraphValidationError("metadata record must be a mapping")
        record = _ImmutableRecord(dict(source_record))
        key = _record_key(record)
        content = _canonical(dict(record))
        previous = seen.get(key)
        if previous is not None and previous != content:
            raise GraphValidationError("same id and revision has different content")
        if previous is not None:
            continue
        seen[key] = content
        MetadataGraph._validate_dimensions(record)
        normalized.append(record)
    return tuple(normalized)


def _normalize_relations(
    relations: Iterable[tuple[str, str, str]],
    record_ids: set[str],
) -> tuple[tuple[str, str, str], ...]:
    normalized = tuple(tuple(relation) for relation in relations)
    if any(len(relation) != 3 for relation in normalized):
        raise GraphValidationError("relation requires subject, predicate, object")
    for subject, _predicate, object_id in normalized:
        if subject not in record_ids or object_id not in record_ids:
            raise GraphValidationError("relation endpoint does not exist")
    MetadataGraph._reject_provenance_cycles(normalized)
    return normalized


class MetadataGraph:
    """Immutable descriptive graph for scientific metadata snapshots."""

    is_executable = False

    def __init__(
        self,
        records: tuple[Mapping[str, Any], ...],
        relations: tuple[tuple[str, str, str], ...],
    ) -> None:
        self.records = records
        self._relations = relations
        self._by_key = {
            _record_key(record): record for record in records
        }
        self._by_id: dict[str, list[Mapping[str, Any]]] = {}
        for record in records:
            self._by_id.setdefault(record["id"], []).append(record)
        for versions in self._by_id.values():
            versions.sort(key=lambda record: record.get("revision", 1))
        identity_payload = {
            "records": sorted(
                (dict(record) for record in records),
                key=lambda record: _canonical(record),
            ),
            "relations": sorted(relations),
        }
        self.identity = hashlib.sha256(_canonical(identity_payload).encode()).hexdigest()

    @classmethod
    def from_records(
        cls,
        records: Iterable[Mapping[str, Any]],
        *,
        relations: Iterable[tuple[str, str, str]] = (),
    ) -> "MetadataGraph":
        normalized = _normalize_records(records)
        normalized_relations = _normalize_relations(
            relations,
            {record["id"] for record in normalized},
        )
        return cls(normalized, normalized_relations)

    @staticmethod
    def _validate_dimensions(record: Mapping[str, Any]) -> None:
        unit = record.get("unit")
        dimension = record.get("dimension")
        if unit is not None and dimension is not None:
            expected = _UNIT_DIMENSIONS.get(unit)
            if expected is not None and expected != dimension:
                raise GraphValidationError("unit and dimension do not agree")

    @staticmethod
    def _reject_provenance_cycles(relations: tuple[tuple[str, str, str], ...]) -> None:
        graph: dict[str, list[str]] = {}
        for subject, predicate, object_id in relations:
            if predicate in {"derived_from", "generated_by"}:
                graph.setdefault(subject, []).append(object_id)

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visiting:
                raise ProvenanceCycleError("provenance derivation cycle")
            if node in visited:
                return
            visiting.add(node)
            for child in graph.get(node, ()):
                visit(child)
            visiting.remove(node)
            visited.add(node)

        for node in graph:
            visit(node)

    def profiles(self) -> tuple[str, ...]:
        return tuple(record["profile"] for record in self.records if "profile" in record)

    def observation_kinds(self, prefix: str = "") -> tuple[str, ...]:
        return tuple(
            record["observation_kind"]
            for record in self.records
            if record.get("id", "").startswith(prefix) and "observation_kind" in record
        )

    def value(self, identifier: str) -> Any:
        record = self._latest(identifier)
        return record.get("value")

    def approval(self, identifier: str) -> Any:
        return self._latest(identifier).get("approval")

    def evidence_for(self, identifier: str) -> tuple[str, ...]:
        return tuple(
            object_id
            for subject, predicate, object_id in self._relations
            if subject == identifier and predicate in {"supported_by", "refuted_by"}
        )

    def correction_lineage(self, identifier: str) -> tuple[str, ...]:
        record = self._latest(identifier)
        original = record.get("derived_from")
        if not isinstance(original, str):
            return (f"{record['id']}@{record.get('revision', 1)}",)
        base_id, _, base_revision = original.rpartition("@")
        if not base_id or not base_revision.isdigit():
            raise GraphValidationError("correction lineage requires id@revision")
        versions = self._by_id.get(base_id, ())
        latest = max((item.get("revision", 1) for item in versions), default=int(base_revision))
        return (original, f"{base_id}@{latest}")

    def _latest(self, identifier: str) -> Mapping[str, Any]:
        try:
            return self._by_id[identifier][-1]
        except KeyError as error:
            raise GraphValidationError(f"unknown metadata id: {identifier}") from error
