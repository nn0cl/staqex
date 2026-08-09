"""Live QPU submit entrypoint (ADR 0203, LISS-0393).

Separate from `host.py`'s `submit_source` / `submit_path`, which are
local-only and synchronous by contract (unchanged, unaffected by this
module). Live QPU submission is fire-and-forget: this function compiles
source, emits QASM3, and submits through an injected `QpuSubmitPort`,
returning `ProviderJobId` immediately -- never `Job`/`JobResult`. Status
and results are separate, explicit `QpuJobPort` calls, unchanged.

This module never imports a concrete provider SDK and never performs a
real submission itself -- `adapter` is always caller-injected (production
callers pass a real adapter such as `AwsBraketAdapter`; tests pass a
fake).
"""

from __future__ import annotations

import hashlib
from typing import Any, Mapping
from uuid import uuid4

from .ast_nodes import DynamicQpuStmt
from .backend.qasm.dynamic_emitter import emit_dynamic_qpu_qasm3
from .backend.qasm.emitter import QASM3Emitter
from .pipeline import compile_source
from .qpu_submit import ProviderJobId, QpuArtifact, QpuSubmitPort, QpuSubmitRequest


def _unit_has_dynamic_qpu(unit: Any) -> bool:
    if unit is None or unit.main is None:
        return False
    return any(isinstance(stmt, DynamicQpuStmt) for stmt in unit.main.body.stmts)


def submit_live_qpu(
    source: str,
    *,
    adapter: QpuSubmitPort,
    execution_settings: Mapping[str, Any] | None = None,
    idempotency_key: str | None = None,
    target_profile: str = "live-qpu",
) -> tuple[ProviderJobId | None, tuple[dict[str, object], ...]]:
    """Compile, emit QASM3, and submit through an injected QpuSubmitPort.

    Returns (ProviderJobId, ()) on success, or (None, diagnostics) if
    compilation or QASM emission failed -- mirrors
    `host.prepare_parametric_qasm`'s existing (payload | None,
    diagnostics) shape. Adapter-level failures (e.g. missing credentials)
    propagate as exceptions, unchanged, since the injected adapter's own
    `submit` already raises for those.
    """

    compiled = compile_source(source)
    if compiled.unit is None:
        return None, tuple(compiled.diagnostics)

    if _unit_has_dynamic_qpu(compiled.unit):
        dynamic_result = emit_dynamic_qpu_qasm3(compiled.unit)
        if not dynamic_result.ok:
            return None, tuple(
                {"code": "DYN_QASM_EMISSION_ERROR", "message": note}
                for note in dynamic_result.notes
            )
        qasm = dynamic_result.qasm
    else:
        static_result = QASM3Emitter().emit_unit(compiled.unit)
        if not static_result.ok:
            return None, tuple(
                {"code": "QASM_EMISSION_ERROR", "message": note}
                for note in static_result.notes
            )
        qasm = static_result.qasm

    content_hash = hashlib.sha256(qasm.encode()).hexdigest()
    artifact = QpuArtifact(
        qasm=qasm,
        target_profile=target_profile,
        provenance={"source": "submit_live_qpu"},
        content_hash=content_hash,
    )
    request = QpuSubmitRequest(
        artifact=artifact,
        execution_settings=dict(execution_settings or {}),
        idempotency_key=idempotency_key or uuid4().hex,
    )
    job_id = adapter.submit(request)
    return job_id, ()


__all__ = ["submit_live_qpu"]
