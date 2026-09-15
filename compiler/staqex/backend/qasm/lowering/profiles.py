"""Immutable target capability facts."""
from .legacy import EvolutionTargetProfile as _LegacyEvolutionTargetProfile


class EvolutionTargetProfile(_LegacyEvolutionTargetProfile):
    """Compatibility-owned target profile during bounded extraction."""
