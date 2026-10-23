"""Canonical semantic identity and serialization."""
from __future__ import annotations
import hashlib
import json

__all__ = ["ScientificSemanticIR", "annotations", "semantic_fingerprint"]
from .model import ScientificSemanticIR

def semantic_fingerprint(core: ScientificSemanticIR) -> str:
    """Return a stable digest for the complete canonical semantic payload."""
    payload = {
        "schema": core.schema,
        "authority": core.authority,
        "has_explicit_realize": core.has_explicit_realize,
        "nodes": [
            {
                "node_id": node.node_id,
                "kind": node.kind,
                "children": node.children,
                "role_lane": node.role_lane,
                "type": node.type,
                "dimensions": node.dimensions,
                "exactness": node.exactness,
                "intent": node.intent,
                "provenance": node.provenance,
                "meaning_kind": node.meaning_kind,
                "state_role": node.state_role,
                "child_source_node_ids": node.child_source_node_ids,
                "control_source_node_id": node.control_source_node_id,
                "branch_rules": node.branch_rules,
                "phase_metadata": node.phase_metadata,
                "branch_relationship": node.branch_relationship,
                "product_kind": node.product_kind,
            }
            for node in core.nodes
        ],
        "relations": [
            {"kind": relation.kind, "node_ids": relation.node_ids}
            for relation in core.relations
        ],
        "lowering_policy": core.lowering_policy,
        "explicit_evolution": core.explicit_evolution,
        "realize_source_node_id": core.realize_source_node_id,
        "finite_realization_record": core.finite_realization_record,
        "binder_lowering": core.binder_lowering,
        "binder_source_node_ids": core.binder_source_node_ids,
        "binder_provenance": core.binder_provenance,
        "projection_errors": core.projection_errors,
        "qpu_projection": None
        if core.qpu_projection is None
        else {
            "logical_qubits": core.qpu_projection.logical_qubits,
            "operations": [
                {
                    "kind": operation.kind,
                    "provenance": operation.provenance,
                    "source_node_id": operation.source_node_id,
                    "opcode": operation.opcode,
                    "qubits": operation.qubits,
                    "parameter": operation.parameter,
                    "size": operation.size,
                    "control": operation.control,
                    "control_width": operation.control_width,
                    "target_offset": operation.target_offset,
                    "inverse": operation.inverse,
                }
                for operation in core.qpu_projection.operations
            ],
            "projection_error": core.qpu_projection.projection_error,
        },
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), default=str
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

