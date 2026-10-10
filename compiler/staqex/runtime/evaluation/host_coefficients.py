"""Resolve declared Host coefficient arrays through existing scientific validation."""

from __future__ import annotations

from typing import Any, Protocol

from ...ast_nodes import CompilationUnit
from ...host_input_port import HostInputPort
from .errors import KernelDiagnosticError


class HostCoefficientContext(Protocol):
    """Live Host input owned by the Evaluator, without a second state store."""

    host_input: HostInputPort | None


def resolve_host_coefficient_arrays(
    context: HostCoefficientContext, unit: CompilationUnit
) -> dict[str, Any]:
    """Resolve declared Float/Bool tensors, preserving validation and merge order."""
    from ...finite_binder import _host_placeholder_keys, merge_host_coefficient_arrays
    from ...scientific_input import (
        CoefficientTensor,
        InputProvenance,
        ScientificInputValidationError,
    )

    placeholders = _host_placeholder_keys(unit)
    if not placeholders:
        return {}
    host_tensors: dict[str, Any] = {}
    for _local_name, (host_key, shape, dtype) in placeholders.items():
        if host_key in host_tensors:
            continue
        raw = context.host_input.get(host_key) if context.host_input is not None else None
        if raw is None:
            continue  # merge_host_coefficient_arrays reports HOST_COEFFICIENT_MISSING
        try:
            host_tensors[host_key] = CoefficientTensor(
                name=host_key,
                shape=shape,
                values=raw,
                provenance=InputProvenance(
                    source_formula="HostInputPort", input_id=host_key
                ),
                dtype=dtype,
            )
        except ScientificInputValidationError as error:
            raise KernelDiagnosticError(error.code, str(error)) from error
    arrays, diagnostics = merge_host_coefficient_arrays(unit, host_tensors)
    if diagnostics:
        first = diagnostics[0]
        raise KernelDiagnosticError(first["code"], first["message"])
    return arrays
