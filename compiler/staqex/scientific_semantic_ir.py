"""Stable public facade for the source-derived Scientific Semantic IR."""

from .scientific_semantic.model import (
    CanonicalQpuOperation, CanonicalQpuProjection, FiniteRealizationRecord,
    IdealMeaning, RealizationProvenance, RuntimeBinderNode,
    RuntimeCallableNode, RuntimeControlNode, RuntimeDynamicLaneNode,
    RuntimeEvolutionNode, RuntimeExecutionPlan, RuntimePlanNode,
    RuntimeTransformationNode, ScientificSemanticIR, SemanticInspectionResult,
    SemanticNode, SemanticProvenance, SemanticRejection, SemanticRelation,
)
from .scientific_semantic.fingerprint import semantic_fingerprint
from .scientific_semantic.builder import build_inspection, build_rejection, build_scientific_semantic_ir
from .scientific_semantic.runtime_plan import build_runtime_execution_plan
from .scientific_semantic.qpu_projection import build_explicit_evolution, build_lowering_policy, build_qpu_projection
from .scientific_semantic.realization import build_algorithm_plan, build_finite_realization_record
from .scientific_semantic.legacy import (
    MIXTURE_PROJECTION_REJECTION_CODE, MIXTURE_PROJECTION_REJECTION_REASON,
    QPU_PROJECTION_MAX_QUBITS,
)
