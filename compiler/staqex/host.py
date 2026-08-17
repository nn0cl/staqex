"""Provider-neutral host Job boundary (LISS-0022, ADR-0065).

This module deliberately converts Kernel results into host DTOs.  Callers do
not receive the evaluator's Joint, AST, or provider-specific objects.

ADR 0198 / LISS-0384 adds an additive ``dynamic_trace`` channel for Dynamic
QPU mid-circuit controller reports; those must not appear as
``MeasurementEnvelope`` entries.

LISS-0383 wires Fake-gated Host submit under ``dynamic_fake_profile`` +
supplied outcomes into ``dynamic_trace`` without claiming physical execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from types import MappingProxyType
from typing import Any, Mapping, TextIO
from uuid import uuid4

from .backend.qasm.emitter import QASM3Emitter
from .parametric_binding import (
    extract_circuit_parameters,
    validate_parameter_bindings,
)
from .dynamic_fake_wire import (
    FAKE_BYPASS_HARD_CODES,
    build_dynamic_exec_request,
    resolve_fake_dynamic_profile,
    unit_has_dynamic_qpu,
)
from .dynamic_qpu import DynamicExecResult, FakeDynamicExecutor
from .host_input_port import MappingHostInputAdapter
from .pipeline import HARD_CODES, CompileResult, compile_path, compile_source
from .runtime.evaluator import EvalResult, Evaluator, KernelDiagnosticError, KernelError
from .observation import ObservationReport


@dataclass(frozen=True)
class MeasurementEnvelope:
    """Opaque host representation of one terminal measurement."""

    value: Any | None
    marginal: dict[Any, float]
    vacuum: bool
    sink: str | None
    output: str


@dataclass(frozen=True)
class DynamicTraceReport:
    """Host report for one Dynamic QPU run (ADR 0198 / LISS-0384).

    Mid-circuit controller bindings live here — never as MeasurementEnvelope.
    """

    lane: str
    profile_id: str
    controller_bindings: Mapping[str, str]
    consumed_token_ids: tuple[str, ...]
    selected_arm: str | None
    physical_execution_claimed: bool
    # LISS-0389 (ADR 0198 Amendment): False only when the real local
    # evaluator positively determined a recorded controller binding was
    # physically unreachable (the run vacuumed). True (default) otherwise,
    # including when nothing has checked yet (e.g. no live provider today).
    physical_outcome_confirmed: bool = True


@dataclass(frozen=True)
class JobResult:
    """Provider-neutral result returned after a Job reaches a terminal state."""

    status: str
    measurements: tuple[MeasurementEnvelope, ...] = ()
    diagnostics: tuple[dict[str, Any], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    # Keep observations before dynamic_trace so pre-observation positional
    # construction (LISS-0046) remains valid; dynamic_trace is trailing.
    observations: tuple[ObservationReport, ...] = ()
    dynamic_trace: DynamicTraceReport | None = None


def project_dynamic_trace(
    exec_result: DynamicExecResult,
    *,
    lane: str,
    profile_id: str,
) -> DynamicTraceReport:
    """Project a Fake/dynamic exec result into the Host dynamic_trace channel."""

    return DynamicTraceReport(
        lane=lane,
        profile_id=profile_id,
        controller_bindings=MappingProxyType(dict(exec_result.controller_bindings)),
        consumed_token_ids=tuple(exec_result.consumed_tokens),
        selected_arm=exec_result.selected_arm,
        physical_execution_claimed=bool(exec_result.physical_execution_claimed),
    )


class Job:
    """A completed local Job with the same surface used by future adapters."""

    def __init__(self, job_id: str, result: JobResult) -> None:
        self.id = job_id
        self._result = result

    def status(self) -> str:
        return self._result.status

    def wait(self) -> JobResult:
        return self._result

    def result(self) -> JobResult:
        return self._result

    def cancel(self) -> str:
        if self._result.status in {"queued", "running"}:
            return "accepted"
        return "already-complete"


def submit_source(
    source: str,
    *,
    settings: dict[str, Any] | None = None,
    stdout: TextIO | None = None,
) -> Job:
    """Submit source to the local adapter and return a provider-neutral Job."""

    settings = dict(settings or {})
    job_id = f"local-{uuid4().hex}"
    return _submit_compiled(
        compile_source(source), settings=settings, stdout=stdout, job_id=job_id
    )


def submit_path(
    entry: str,
    *,
    settings: dict[str, Any] | None = None,
    stdout: TextIO | None = None,
) -> Job:
    """Submit a linked source path through the same local Job adapter."""

    settings = dict(settings or {})
    job_id = f"local-{uuid4().hex}"
    return _submit_compiled(
        compile_path(entry), settings=settings, stdout=stdout, job_id=job_id
    )


def _submit_allows_execution(
    compiled: CompileResult,
    *,
    fake_profile: str | None,
) -> bool:
    """Whether Host may run Local/Fake evaluation for this compile result."""

    if compiled.unit is None:
        return False
    blocking = any(
        d.get("code") in HARD_CODES and d.get("code") not in FAKE_BYPASS_HARD_CODES
        for d in compiled.diagnostics
    )
    if blocking:
        return False
    # Target capability diagnostics describe a QPU realization boundary; they
    # do not prevent the local simulator from executing the source meaning.
    if fake_profile is not None and unit_has_dynamic_qpu(compiled.unit):
        return True
    return True


def _submit_compiled(
    compiled: CompileResult,
    *,
    settings: dict[str, Any],
    stdout: TextIO | None,
    job_id: str,
) -> Job:
    fake_profile = resolve_fake_dynamic_profile(settings)
    if not _submit_allows_execution(compiled, fake_profile=fake_profile):
        return Job(
            job_id,
            JobResult(
                status="failed",
                diagnostics=tuple(compiled.diagnostics),
                metadata={"target": settings.get("target", "local")},
            ),
        )

    assert compiled.unit is not None
    dynamic_trace: DynamicTraceReport | None = None

    if fake_profile is not None and unit_has_dynamic_qpu(compiled.unit):
        outcomes = settings.get("dynamic_supplied_outcomes") or {}
        if not isinstance(outcomes, Mapping):
            outcomes = {}
        request = build_dynamic_exec_request(
            compiled.unit,
            profile_id=fake_profile,
            supplied_outcomes_by_controller=outcomes,
        )
        if request is None:
            return Job(
                job_id,
                JobResult(
                    status="failed",
                    diagnostics=tuple(compiled.diagnostics)
                    + (
                        {
                            "code": "DYN_FAKE_REQUEST_BUILD_FAILED",
                            "message": "Fake gate present but no mid-circuit tokens",
                        },
                    ),
                    metadata={"target": settings.get("target", "local")},
                ),
            )
        try:
            fake_result = FakeDynamicExecutor().execute(request)
        except KeyError as exc:
            return Job(
                job_id,
                JobResult(
                    status="failed",
                    diagnostics=tuple(compiled.diagnostics)
                    + (
                        {
                            "code": "DYN_SUPPLIED_OUTCOME_MISSING",
                            "message": f"missing supplied outcome for token {exc}",
                        },
                    ),
                    metadata={"target": settings.get("target", "local")},
                ),
            )
        if fake_result.status != "accepted":
            fake_diagnostics = [
                {"code": d.code, "message": d.message} for d in fake_result.diagnostics
            ]
            return Job(
                job_id,
                JobResult(
                    status="failed",
                    diagnostics=tuple(compiled.diagnostics) + tuple(fake_diagnostics),
                    metadata={"target": settings.get("target", "local")},
                    dynamic_trace=None,
                ),
            )
        dynamic_trace = project_dynamic_trace(
            fake_result,
            lane=request.lane,
            profile_id=fake_profile,
        )

    try:
        inputs = dict(settings.get("inputs") or {})
        if fake_profile is not None and unit_has_dynamic_qpu(compiled.unit):
            # LISS-0387 (ADR 0200 Decision 2): route the same supplied
            # outcomes Host already verified via FakeDynamicExecutor above
            # into the Kernel's HostInputPort channel (ADR 0194), so the
            # evaluator's real mid-circuit collapse uses the identical data.
            supplied_by_controller = settings.get("dynamic_supplied_outcomes") or {}
            if isinstance(supplied_by_controller, Mapping):
                for controller_name, outcome in supplied_by_controller.items():
                    inputs[f"dynamic:{controller_name}"] = outcome
        host_input = MappingHostInputAdapter(inputs) if inputs else None
        evaluator = Evaluator(
            seed=settings.get("seed"),
            grid_hamiltonians=dict(compiled.grid_hamiltonians or {}),
            data_parallel_workers=int(settings.get("data_parallel_workers") or 1),
            host_input=host_input,
        )
        evaluated = evaluator.run_unit(compiled.unit, stdout=stdout)
        if dynamic_trace is not None:
            # LISS-0389 (ADR 0198 Amendment): reconcile Host's bookkeeping
            # dynamic_trace with what the real evaluator actually found.
            dynamic_trace = replace(
                dynamic_trace,
                physical_outcome_confirmed=evaluated.dynamic_outcomes_confirmed,
            )
    except KernelDiagnosticError as exc:
        metadata = {"target": settings.get("target", "local")}
        if exc.provenance is not None:
            metadata["evolution_provenance"] = dict(exc.provenance)
        return Job(
            job_id,
            JobResult(
                status="failed",
                diagnostics=(
                    {
                        "code": exc.code,
                        "message": str(exc),
                        "line": exc.line,
                        "col": exc.col,
                    },
                ),
                metadata=metadata,
                dynamic_trace=dynamic_trace,
            ),
        )
    except KernelError as exc:
        return Job(
            job_id,
            JobResult(
                status="failed",
                diagnostics=({"code": "RUNTIME_ERROR", "message": str(exc)},),
                metadata={"target": settings.get("target", "local")},
                dynamic_trace=dynamic_trace,
            ),
        )

    measurement = _measurement_envelope(evaluated)
    measurements = () if measurement is None else (measurement,)
    metadata = {"target": settings.get("target", "local")}
    if evaluated.evolution_provenance is not None:
        metadata["evolution_provenance"] = dict(evaluated.evolution_provenance)
    if evaluated.mixed_state_measured:
        metadata["state_type"] = "DensityState"
        metadata["execution_lane"] = evaluated.execution_lane or "cpu/simulator"
    if evaluated.measurement_kind is not None:
        metadata["measurement_kind"] = evaluated.measurement_kind
    return Job(
        job_id,
        JobResult(
            status="succeeded",
            measurements=measurements,
            diagnostics=tuple(compiled.diagnostics),
            metadata=metadata,
            dynamic_trace=dynamic_trace,
        ),
    )


def run_source(
    source: str,
    *,
    settings: dict[str, Any] | None = None,
    stdout: TextIO | None = None,
) -> JobResult:
    """Blocking convenience API equivalent to submit followed by result."""

    return submit_source(source, settings=settings, stdout=stdout).result()


def run_path(
    entry: str,
    *,
    settings: dict[str, Any] | None = None,
    stdout: TextIO | None = None,
) -> JobResult:
    """Blocking convenience API for a linked source path."""

    return submit_path(entry, settings=settings, stdout=stdout).result()


def prepare_parametric_qasm(
    compiled: CompileResult,
    bindings: dict[str, float] | None = None,
    *,
    route: bool = False,
) -> tuple[str | None, tuple[dict[str, object], ...]]:
    """Validate Host bindings and emit provider-neutral OpenQASM when possible."""

    if compiled.unit is None or not compiled.ok:
        return None, tuple(compiled.diagnostics)

    declared = extract_circuit_parameters(compiled.unit)
    binding_map = dict(bindings or {})
    diagnostics = validate_parameter_bindings(declared, binding_map)
    if diagnostics:
        return None, diagnostics

    program = compiled.qpu_ir
    if program is None:
        return None, (
            {
                "code": "QPU_IR_UNAVAILABLE",
                "message": "compiled source has no provider-neutral QPU IR",
            },
        )

    emitted = QASM3Emitter(route=route).emit_qpu_program(
        program,
        parameter_values=binding_map or None,
    )
    if not emitted.ok:
        return None, tuple({"code": "QASM_EMISSION_ERROR", "message": note} for note in emitted.notes)
    return emitted.qasm, ()


def _measurement_envelope(evaluated: EvalResult) -> MeasurementEnvelope | None:
    measured = evaluated.measure
    if measured is None:
        return None
    return MeasurementEnvelope(
        value=measured.value,
        marginal=dict(measured.marginal),
        vacuum=measured.vacuum,
        sink=measured.sink,
        output=measured.output,
    )
