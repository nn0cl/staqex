"""Phase 1 Red contract for the finite-binder compatibility facade."""

from compiler.staqex import finite_binder, finite_binder_legacy
from compiler.staqex.finite_binder import (
    _collect_float_arrays,
    _contains_binder,
    _host_placeholder_keys,
    _lower_operator_expr,
)


def test_facade_reexports_legacy_runtime_helpers():
    """The facade must preserve private helpers used by existing consumers."""

    for name in (
        "_collect_float_arrays",
        "_contains_binder",
        "_host_placeholder_keys",
        "_lower_operator_expr",
    ):
        assert getattr(finite_binder, name) is getattr(finite_binder_legacy, name)
