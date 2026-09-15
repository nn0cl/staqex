"""Stable public facade for QASM lowering compatibility."""

from .lowering.legacy import *  # noqa: F401,F403
from .lowering.profiles import EvolutionTargetProfile
from .lowering.preflight import (
    explicit_evolution_capability_reject,
    formal_limit_capability_reject,
    qudit_capability_reject,
)
from .lowering.evolution import (
    lower_explicit_evolve,
    lower_formal_limit,
    lower_evolve_under,
)
from .lowering.resources import register_resource_budget_reject
from .lowering.semantic import lower_semantic_to_circuit
from .lowering.ast_compat import lower_ast_compat
