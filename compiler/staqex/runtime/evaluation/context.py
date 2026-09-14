"""Explicit context contracts for extracted evaluator services."""

from __future__ import annotations

from typing import Any, Protocol, TextIO

from ...ast_nodes import CompilationUnit


class EvaluatorContext(Protocol):
    """The single live state owner exposed to evaluation services.

    The protocol describes orchestration callbacks rather than copying the
    evaluator's mutable maps. Concrete state remains owned by ``Evaluator``.
    """

    def _execute_evolution_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _execute_control_mixture_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _execute_pure_transformation_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _execute_binder_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _execute_callable_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _execute_dynamic_lane_plan(
        self, plan: Any, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _is_first_runtime_family(self, unit: CompilationUnit, plan: Any) -> bool: ...

    def _execute_first_runtime_family(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _run_legacy_ast_body(
        self, unit: CompilationUnit, *, stdout: TextIO | None = None
    ) -> Any: ...

    def _evaluate_value(self, expr: Any, assign: dict[str, Any]) -> Any: ...

    def _resolve_operator(self, expr: Any) -> Any: ...

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
