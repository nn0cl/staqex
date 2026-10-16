"""Operator-family entrypoint during incremental extraction."""

from __future__ import annotations

from typing import Any

from .context import TypeCheckContext
from ..ast_nodes import (
    OpBinder,
    IndexDomain,
    RevDomain,
    TypeRef,
    OpBin,
    OpIndexed,
    OpVar,
    OpLit,
    OpCall,
    OpExpr,
)
from .operator_context import OperatorCheckContext, OperatorTypeView


def check_operator_expr(
    context: TypeCheckContext, *args: Any, **kwargs: Any
) -> Any:
    """Delegate operator checks without changing diagnostic ownership."""
    return context._legacy_check_operator(*args, **kwargs)


def _legacy_check_operator(self: OperatorCheckContext, expr: OpExpr) -> None:
    """Check a symbolic operator tree without expanding or executing it."""
    if isinstance(expr, OpBinder):
        domain_ty: OperatorTypeView | None = None
        if isinstance(expr.domain, (IndexDomain, RevDomain)):
            self._check_index_domain_expr(expr.domain)
            domain_ty = self._operator_index_type()
        elif isinstance(expr.domain, TypeRef):
            if expr.domain.name == "Basis":
                if not self._valid_basis_domain(expr.domain):
                    self.diagnostics.append(
                        {
                            "code": "BINDER_DOMAIN_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": (
                                "`Basis<N>` binder domain requires a static "
                                "non-negative integer size"
                            ),
                        }
                    )
                else:
                    size = int(expr.domain.args[0].name)
                    if size == 0:
                        self.diagnostics.append(
                            {
                                "code": "EMPTY_BINDER_DOMAIN_WARNING",
                                "line": expr.span.line,
                                "col": expr.span.col,
                                "message": (
                                    "Basis binder domain is empty; "
                                    "using the fold identity"
                                ),
                            }
                        )
                    end = size - 1
                    capacity = max(
                        (
                            value
                            for name, value in self.semantic_values.items()
                            if self.env.get(name) is not None
                            and self.env[name].kind == "Register"
                        ),
                        default=None,
                    )
                    if capacity is not None and size > 0 and end >= capacity:
                        self.diagnostics.append(
                            {
                                "code": "BINDER_DOMAIN_ERROR",
                                "line": expr.span.line,
                                "col": expr.span.col,
                                "message": (
                                    "Basis binder domain exceeds the static "
                                    "register shape"
                                ),
                            }
                        )
            elif expr.domain.name != "Index":
                self.diagnostics.append(
                    {
                        "code": "BINDER_DOMAIN_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            f"binder domain `{expr.domain.name}` is not a finite "
                            "`Index` or `Basis` range; other carriers remain deferred"
                        ),
                    }
                )
            elif not self._valid_index_domain(expr.domain):
                self.diagnostics.append(
                    {
                        "code": "BINDER_DOMAIN_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": "`Index<N>` or inclusive `Index<start..end>` requires static bounds",
                    }
                )
            elif expr.domain.is_inclusive_range:
                start = int(expr.domain.args[0].name)
                end = int(expr.domain.args[1].name)
                if end < start:
                    self.diagnostics.append(
                        {
                            "code": "EMPTY_BINDER_DOMAIN_WARNING",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": "inclusive binder range is empty; using the fold identity",
                        }
                    )
                capacity = max(
                    (
                        value
                        for name, value in self.semantic_values.items()
                        if self.env.get(name) is not None
                        and self.env[name].kind == "Register"
                    ),
                    default=None,
                )
                if capacity is not None and end >= capacity:
                    self.diagnostics.append(
                        {
                            "code": "BINDER_DOMAIN_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": "inclusive binder range exceeds the static register shape",
                        }
                    )
            domain_ty = self._ty_from_ref(expr.domain)
        else:
            domain_ty = self.env.get(expr.domain.name)
            if domain_ty is None:
                self.diagnostics.append(
                    {
                        "code": "BINDER_DOMAIN_ERROR",
                        "line": expr.domain.span.line,
                        "col": expr.domain.span.col,
                        "message": f"unknown finite binder domain `{expr.domain.name}`",
                    }
                )
            elif domain_ty.kind == "Execution":
                self.diagnostics.append(
                    {
                        "code": "PHASE_TYPE_VISIBILITY_ERROR",
                        "line": expr.domain.span.line,
                        "col": expr.domain.span.col,
                        "message": f"execution carrier `{domain_ty}` cannot be a theory domain",
                    }
                )
            elif domain_ty.kind not in {"Meta", "Discrete"} and not (
                # LISS-0430: `Sigma (x In F)` where F is a `Set`
                # comprehension value (LISS-0429) -- a genuinely
                # finite, enumerable domain, just not the pre-existing
                # Index/Basis-shaped one this check was written for.
                # `F`'s own declared-type inference lands on
                # `Ty("State", "Set", ...)` (the generic Type-First
                # fallback for an unrecognized type head wraps
                # `_infer`'s payload in State kind, confirmed by
                # reading `checker.env` directly, not assumed) rather
                # than the `Ty("Classical", "Set", ...)`
                # `_infer_inner`'s own `SetComprehension` case returns
                # -- checking `payload == "Set"` alone is the
                # reliable signal.
                domain_ty.payload == "Set"
            ):
                self.diagnostics.append(
                    {
                        "code": "BINDER_DOMAIN_ERROR",
                        "line": expr.domain.span.line,
                        "col": expr.domain.span.col,
                        "message": f"`{expr.domain.name}` is not a finite semantic domain",
                    }
                )
            if self.semantic_values.get(expr.domain.name, 0) > 1_000_000:
                self.diagnostics.append(
                    {
                        "code": "BINDER_RESOURCE_ERROR",
                        "line": expr.domain.span.line,
                        "col": expr.domain.span.col,
                        "message": "finite binder expansion exceeds the Kernel resource budget",
                    }
                )
        previous = self.env.get(expr.variable)
        if (
            isinstance(expr.domain, TypeRef)
            and expr.domain.name == "Basis"
            and self._valid_basis_domain(expr.domain)
        ):
            self.env[expr.variable] = self._ty_from_ref(expr.domain)
        else:
            self.env[expr.variable] = self._operator_index_type()
        self._binder_depth += 1
        try:
            self._check_operator_expr(expr.body)
            self._require_full_rank_coeff(expr.body)
        finally:
            self._binder_depth -= 1
        if previous is None:
            self.env.pop(expr.variable, None)
        else:
            self.env[expr.variable] = previous
        return

    if isinstance(expr, OpBin):
        self._check_operator_expr(expr.lhs)
        self._check_operator_expr(expr.rhs)
        if self._binder_depth > 0:
            self._require_full_rank_coeff(expr.lhs)
            self._require_full_rank_coeff(expr.rhs)
        return
    if isinstance(expr, OpIndexed):
        self._check_operator_expr(expr.base)
        self._check_operator_expr(expr.index)
        if (
            self._binder_depth > 0
            and isinstance(expr.base, OpVar)
            and expr.base.name not in {"create", "annihilate"}
            and expr.base.name not in self.float_arrays
        ):
            self.diagnostics.append(
                {
                    "code": "BINDER_LOWERING_UNSUPPORTED",
                    "line": expr.base.span.line,
                    "col": expr.base.span.col,
                    "message": (
                        f"indexed coefficient `{expr.base.name}[…]` requires a "
                        "`Float[N]…` binding (or a second-quantized atom)"
                    ),
                }
            )
        if isinstance(expr.index, OpVar):
            index_ty = self.env.get(expr.index.name)
            if index_ty is not None and index_ty.kind == "Execution":
                self.diagnostics.append(
                    {
                        "code": "PHASE_TYPE_VISIBILITY_ERROR",
                        "line": expr.index.span.line,
                        "col": expr.index.span.col,
                        "message": "execution carrier cannot index a theory operator",
                    }
                )
        if (
            self._active_register_set is not None
            and isinstance(expr.index, OpLit)
            and len(self.system_registers.get(self._active_register_set, ())) > 1
        ):
            # LISS-0133: `data[0]` building blocks are register-qualified;
            # only bare operator sites like `Z[0]` are ambiguous.
            registers = dict(
                self.system_registers.get(self._active_register_set, ())
            )
            base_is_register = (
                isinstance(expr.base, OpVar) and expr.base.name in registers
            )
            if not base_is_register:
                self.diagnostics.append(
                    {
                        "code": "MULTI_REGISTER_INDEX_AMBIGUOUS",
                        "line": expr.index.span.line,
                        "col": expr.index.span.col,
                        "message": "multi-register operators require a register-qualified site",
                    }
                )
        if isinstance(expr.index, OpIndexed) and isinstance(expr.index.base, OpVar):
            register_name = expr.index.base.name
            registers = dict(self.system_registers.get(self._active_register_set or "", ()))
            if self._active_register_set is not None and register_name not in registers:
                self.diagnostics.append(
                    {
                        "code": "UNKNOWN_REGISTER_ID",
                        "line": expr.index.span.line,
                        "col": expr.index.span.col,
                        "message": f"unknown register `{register_name}` in acting space",
                    }
                )
        return
    if isinstance(expr, OpCall):
        if expr.name in {"I", "X", "Y", "Z"}:
            self.diagnostics.append(
                {
                    "code": "RETIRED_OPERATOR_INDEX_SYNTAX",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": (
                        f"`{expr.name}(…)` is retired operator-index syntax; "
                        f"write `{expr.name}[…]`"
                    ),
                }
            )
        if expr.name in {"Measure", "log", "write", "send"}:
            self.diagnostics.append(
                {
                    "code": "MATHEMATICAL_BINDER_EFFECT_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": f"`{expr.name}` is not allowed in a mathematical binder",
                }
            )
        for arg in expr.args:
            self._check_operator_expr(arg)
        return
