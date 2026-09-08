"""Host-side typed binding contracts for scientific metadata snapshots."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .scientific_input import (
    CoefficientTensor,
    ParameterBinding,
    ScientificInput,
)


class BindingValidationError(ValueError):
    """A binding cannot preserve the declared scientific meaning."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class BindingContract:
    """Meaning metadata required to bind one Host value."""

    source_symbol: str
    snapshot_id: str
    snapshot_revision: int
    shape: tuple[int, ...]
    axis_map: tuple[str, ...]
    index_map: tuple[tuple[str, tuple[int, ...]], ...]
    unit: str
    dimension_signature: str
    frame: str | None = None
    mapping_kind: str = "identity"


@dataclass(frozen=True)
class DecodedBinding:
    """A decoded value plus the evidence needed to reproduce its meaning."""

    source_symbol: str
    snapshot_id: str
    snapshot_revision: int
    shape: tuple[int, ...]
    axis_map: tuple[str, ...]
    index_map: tuple[tuple[str, tuple[int, ...]], ...]
    semantic_hash: str
    mapping_evidence: tuple[tuple[str, Any], ...]
    value: Any


_UNIT_DIMENSIONS = {
    "rad": "Angle",
    "deg": "Angle",
    "m": "Length",
    "cm": "Length",
    "mm": "Length",
    "s": "Time",
    "ms": "Time",
}
_MAPPING_KINDS = {
    "identity",
    "explicit_unit_conversion",
    "explicit_axis_permutation",
}
BindingValue = ParameterBinding | CoefficientTensor | ScientificInput | Mapping[str, Any]


def bind_input(
    value: BindingValue,
    contract: BindingContract,
    *,
    snapshot: Mapping[str, Any],
    mapping_evidence: Mapping[str, Any] | None = None,
) -> DecodedBinding:
    """Validate and decode a Host value without entering the Kernel."""

    _validate_contract(contract, snapshot)
    source_name, source_unit, source_shape, source_value = _source_details(value)
    _validate_source_identity(contract, value, source_name)
    _validate_shape(contract, source_shape)
    _validate_unit_mapping(contract, source_unit, mapping_evidence)
    evidence = tuple(sorted((mapping_evidence or {}).items()))
    return DecodedBinding(
        source_symbol=contract.source_symbol,
        snapshot_id=contract.snapshot_id,
        snapshot_revision=contract.snapshot_revision,
        shape=contract.shape,
        axis_map=contract.axis_map,
        index_map=contract.index_map,
        semantic_hash=str(snapshot["semantic_hash"]),
        mapping_evidence=evidence,
        value=source_value,
    )


def _validate_contract(
    contract: BindingContract, snapshot: Mapping[str, Any]
) -> None:
    if contract.mapping_kind not in _MAPPING_KINDS:
        raise BindingValidationError(
            "BINDING_MAPPING_KIND_UNSUPPORTED",
            "mapping kind must be explicit and supported",
        )
    snapshot_matches = (
        contract.snapshot_id == snapshot.get("snapshot_id")
        and contract.snapshot_revision == snapshot.get("revision")
    )
    if not snapshot_matches:
        raise BindingValidationError(
            "BINDING_SNAPSHOT_MISMATCH",
            "binding references a stale or different metadata snapshot",
        )
    if contract.unit not in _UNIT_DIMENSIONS:
        raise BindingValidationError(
            "BINDING_UNKNOWN_UNIT",
            f"unknown binding unit: {contract.unit}",
        )
    if _UNIT_DIMENSIONS[contract.unit] != contract.dimension_signature:
        raise BindingValidationError(
            "BINDING_DIMENSION_MISMATCH",
            "binding unit does not match its dimension signature",
        )


def _source_details(
    value: BindingValue,
) -> tuple[str, str | None, tuple[int, ...], Any]:
    if isinstance(value, ParameterBinding):
        return value.name, value.unit, (), value.value
    if isinstance(value, CoefficientTensor):
        return value.name, None, value.shape, value.values
    if isinstance(value, ScientificInput):
        if len(value.bindings) != 1:
            raise BindingValidationError(
                "BINDING_SOURCE_IDENTITY_REQUIRED",
                "binding requires exactly one ScientificInput parameter",
            )
        binding = value.bindings[0]
        return binding.name, binding.unit, (), binding.value
    return "", None, (), value


def _validate_unit_mapping(
    contract: BindingContract,
    source_unit: str | None,
    mapping_evidence: Mapping[str, Any] | None,
) -> None:
    if contract.mapping_kind == "identity":
        if source_unit is not None and source_unit != contract.unit:
            raise BindingValidationError(
                "BINDING_UNIT_MISMATCH",
                "identity binding cannot change units",
            )
        return
    if contract.mapping_kind == "explicit_unit_conversion":
        evidence_matches = (
            mapping_evidence
            and mapping_evidence.get("from") == source_unit
            and mapping_evidence.get("to") == contract.unit
        )
        if not evidence_matches:
            raise BindingValidationError(
                "BINDING_CONVERSION_EVIDENCE_REQUIRED",
                "explicit unit conversion requires matching evidence",
            )
        return
    if not mapping_evidence or mapping_evidence.get("kind") != "explicit":
        raise BindingValidationError(
            "BINDING_AXIS_MISMATCH",
            "axis permutation requires explicit evidence",
        )


def _validate_source_identity(
    contract: BindingContract,
    value: BindingValue,
    source_name: str,
) -> None:
    if not contract.source_symbol.strip() or isinstance(value, Mapping):
        raise BindingValidationError(
            "BINDING_SOURCE_IDENTITY_REQUIRED",
            "a binding requires a source symbol and typed source value",
        )
    if source_name != contract.source_symbol:
        raise BindingValidationError(
            "BINDING_SOURCE_IDENTITY_REQUIRED",
            "source symbol does not match the BindingContract",
        )


def _validate_shape(contract: BindingContract, source_shape: tuple[int, ...]) -> None:
    if source_shape != contract.shape:
        raise BindingValidationError(
            "BINDING_SHAPE_MISMATCH",
            "source shape does not match the BindingContract",
        )
    if len(contract.axis_map) != len(contract.shape):
        raise BindingValidationError(
            "BINDING_AXIS_MISMATCH",
            "axis map does not match source rank",
        )
