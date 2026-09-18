"""Explicit context contracts for extracted evaluator services."""

from __future__ import annotations

from typing import Any, Protocol, TextIO

from ...ast_nodes import CompilationUnit


class EvaluatorContext(Protocol):
    """The single live state owner exposed to evaluation services.

    The protocol describes orchestration callbacks rather than copying the
    evaluator's mutable maps. Concrete state remains owned by ``Evaluator``.
    """

    def _require_runtime_plan_family(
        self, plan: Any, family: str, payload_name: str
    ) -> None: ...

    def _execute_deferred_state_measure_plan(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _main_deferred_eligible(self, statements: list[Any]) -> bool: ...

    def _is_minimal_local_evolution(self, unit: CompilationUnit) -> bool: ...

    def _evolution_runtime_unit(self, unit: CompilationUnit) -> CompilationUnit: ...

    def _binder_runtime_unit(self, unit: CompilationUnit) -> CompilationUnit: ...

    def _is_deferred_callable_eligible(self, unit: CompilationUnit) -> bool: ...

    def _is_first_runtime_family(self, unit: CompilationUnit, plan: Any) -> bool: ...

    def _execute_first_runtime_family(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _run_legacy_ast_body(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _evaluate_value(self, expr: Any, assign: dict[str, Any]) -> Any: ...

    def _resolve_operator(
        self,
        expr: Any,
        *,
        objects: dict[str, Any] | None = None,
        extra_arrays: dict[str, Any] | None = None,
    ) -> Any: ...

    def _execute_evolution(
        self, joint: Any, names: list[str], expr: Any
    ) -> Any: ...

    def _bind_call(self, joint: Any, name: str, expr: Any) -> Any: ...

    def _legacy_evaluate_value(self, expr: Any, assign: dict[str, Any]) -> Any: ...

    def _legacy_resolve_operator(self, expr: Any) -> Any: ...

    def _legacy_hamiltonian_evolve_one_step(
        self, joint: Any, names: list[str], expr: Any
    ) -> Any: ...

    def _legacy_bind_call(self, joint: Any, name: str, expr: Any) -> Any: ...
