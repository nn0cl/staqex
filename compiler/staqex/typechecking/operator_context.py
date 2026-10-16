"""Structural contracts for operator checks over the live TypeChecker state."""

from __future__ import annotations

from typing import Any, Mapping, MutableMapping, MutableSequence, Protocol

from ..ast_nodes import OpExpr, TypeRef, IndexDomain, RevDomain


class OperatorTypeView(Protocol):
    """Read-only presentation used by finite-domain checks."""

    @property
    def kind(self) -> str: ...

    @property
    def payload(self) -> str: ...

    def __str__(self) -> str: ...


class OperatorCheckContext(Protocol):
    """The existing owner supplies state, recursive hooks and fresh Ty values."""

    env: MutableMapping[str, OperatorTypeView]
    diagnostics: MutableSequence[dict[str, Any]]
    semantic_values: Mapping[str, int]
    float_arrays: Mapping[str, tuple[int, ...]]
    system_registers: Mapping[str, tuple[tuple[str, int], ...]]
    _binder_depth: int
    _active_register_set: str | None

    def _operator_index_type(self) -> OperatorTypeView: ...
    def _check_index_domain_expr(self, domain: IndexDomain | RevDomain) -> None: ...
    def _valid_basis_domain(self, ref: TypeRef) -> bool: ...
    def _valid_index_domain(self, ref: TypeRef) -> bool: ...
    def _ty_from_ref(self, ref: TypeRef) -> OperatorTypeView: ...
    def _check_operator_expr(self, expr: OpExpr) -> None: ...
    def _require_full_rank_coeff(self, expr: OpExpr) -> None: ...
