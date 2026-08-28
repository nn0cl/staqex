"""Provider-neutral finite realization contract for the QPU boundary.

This module owns only the explicit finite boundary.  It does not select a
provider, allocate a device, or emit provider payloads.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from .scientific_semantic_ir import ScientificSemanticIR, semantic_fingerprint


@dataclass(frozen=True, slots=True)
class RealizePlan:
    method: str
    order: int
    steps: int
    error_budget: float
    dimensions: tuple[int, ...]
    basis_order: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ArtifactDiagnostic:
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class ExecutionArtifact:
    source_fingerprint: str
    semantic_fingerprint: str
    provenance: dict[str, Any]
    policy: RealizePlan
    approximation: dict[str, Any]
    instructions: tuple[str, ...]
    canonical_bytes: bytes
    fingerprint: str


@dataclass(frozen=True, slots=True)
class ArtifactDecision:
    artifact: ExecutionArtifact | None
    diagnostics: tuple[ArtifactDiagnostic, ...] = ()
    provenance: dict[str, Any] | None = None
    allocation: None = None
    provider_payload: None = None


def _provenance(semantic_ir: ScientificSemanticIR) -> dict[str, Any]:
    record = semantic_ir.finite_realization_record
    source_id = semantic_ir.source_id
    source_path = Path(source_id)
    if source_path.is_absolute():
        try:
            source_id = str(source_path.relative_to(Path.cwd()))
        except ValueError:
            pass
    return {
        "source_id": source_id,
        "source_node_id": (
            record.source_node_id
            if record is not None
            else (semantic_ir.nodes[0].node_id if semantic_ir.nodes else "")
        ),
        "authority": semantic_ir.authority,
    }


def _source_fingerprint(semantic_ir: ScientificSemanticIR, semantic_digest: str) -> str:
    if semantic_ir.ideal_meaning is not None:
        return semantic_ir.ideal_meaning.source_fingerprint
    return semantic_digest


def _rejected(
    provenance: dict[str, Any], code: str, message: str
) -> ArtifactDecision:
    return ArtifactDecision(
        artifact=None,
        diagnostics=(ArtifactDiagnostic(code, message),),
        provenance=provenance,
    )


def _invalid_policy(plan: RealizePlan) -> str | None:
    if plan.method not in {"product", "suzuki"}:
        return "REALIZE_METHOD_UNSUPPORTED"
    if plan.order <= 0 or plan.steps <= 0:
        return "REALIZE_FINITE_POLICY_INVALID"
    if not plan.dimensions or any(
        not isinstance(dimension, int) or isinstance(dimension, bool) or dimension <= 0
        for dimension in plan.dimensions
    ):
        return "REALIZE_DIMENSIONS_INVALID"
    if not all(isinstance(label, str) and label for label in plan.basis_order):
        return "REALIZE_BASIS_ORDER_INVALID"
    if not math.isfinite(plan.error_budget) or plan.error_budget <= 0:
        return "REALIZE_ERROR_BUDGET_INVALID"
    return None


def _canonical_payload(
    *,
    source_fingerprint: str,
    semantic_digest: str,
    provenance: dict[str, Any],
    policy: RealizePlan,
    approximation: dict[str, Any],
    instructions: tuple[str, ...],
) -> bytes:
    payload = {
        "source_fingerprint": source_fingerprint,
        "semantic_fingerprint": semantic_digest,
        "provenance": provenance,
        "policy": {
            "method": policy.method,
            "order": policy.order,
            "steps": policy.steps,
            "error_budget": policy.error_budget,
            "dimensions": policy.dimensions,
            "basis_order": policy.basis_order,
        },
        "approximation": approximation,
        "instructions": instructions,
    }
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")


def build_execution_artifact(
    semantic_ir: ScientificSemanticIR,
    plan: RealizePlan | None = None,
    *,
    instructions: tuple[str, ...] = (),
) -> ArtifactDecision:
    """Build a finite artifact only from an explicit valid realization plan."""

    provenance = _provenance(semantic_ir)
    if plan is None:
        return _rejected(
            provenance,
            "FINITE_REALIZATION_REQUIRED",
            "an explicit finite Realize plan is required",
        )

    invalid_code = _invalid_policy(plan)
    if invalid_code is not None:
        return _rejected(
            provenance, invalid_code, "finite realization policy is invalid"
        )

    semantic_digest = semantic_fingerprint(semantic_ir)
    source_digest = _source_fingerprint(semantic_ir, semantic_digest)
    approximation = {
        "method": plan.method,
        "order": plan.order,
        "steps": plan.steps,
        "error_budget": plan.error_budget,
    }
    canonical_bytes = _canonical_payload(
        source_fingerprint=source_digest,
        semantic_digest=semantic_digest,
        provenance=provenance,
        policy=plan,
        approximation=approximation,
        instructions=tuple(instructions),
    )
    artifact_fingerprint = "sha256:" + hashlib.sha256(canonical_bytes).hexdigest()
    artifact = ExecutionArtifact(
        source_fingerprint=source_digest,
        semantic_fingerprint=semantic_digest,
        provenance=provenance,
        policy=plan,
        approximation=approximation,
        instructions=tuple(instructions),
        canonical_bytes=canonical_bytes,
        fingerprint=artifact_fingerprint,
    )
    return ArtifactDecision(artifact=artifact, provenance=provenance)
