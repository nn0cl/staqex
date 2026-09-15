"""Evolution lowering family."""
from __future__ import annotations
from typing import Any
from . import legacy as _legacy

def lower_explicit_evolve(*args: Any, **kwargs: Any):
    return _legacy._lower_explicit_evolve(*args, **kwargs)

def lower_formal_limit(*args: Any, **kwargs: Any):
    return _legacy._lower_formal_limit(*args, **kwargs)

def lower_evolve_under(*args: Any, **kwargs: Any):
    return _legacy._lower_evolve_under(*args, **kwargs)

