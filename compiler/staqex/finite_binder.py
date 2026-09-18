"""Public compatibility facade for finite-binder lowering.

The legacy module remains the implementation owner.  These explicit private
re-exports preserve runtime consumers that historically imported helper
symbols from this facade; ``import *`` intentionally does not include them.
"""

from .finite_binder_legacy import *  # noqa: F401,F403
from .finite_binder_legacy import (
    _collect_float_arrays,
    _contains_binder,
    _host_placeholder_keys,
    _lower_operator_expr,
)
