"""S02 Host-side BenchmarkResult DTO and builder (LISS-0323 / LISS-0403,
WP-0093 work units D and E).

Maps S02's classical/quantum boundary onto already-shipped Kernel
primitives -- terminal `Measure` and `MeasurementEnvelope.vacuum` -- into
the accepted S02 spec's Result contract. Does not define
`Observable<T>`/`Projection<T>`/`Observation<T>` as Kernel types (WP-0092's
own open decision).

`baseline_score`/`objective_score`/`reranked_score`/`quality_metrics`
were deferred by LISS-0323 ("no S02 `.sqx` program exists yet to produce
them") and are now populated by `benchmark_report.py` (LISS-0403), which
runs `main_selection.sqx` for real and scores its output against the
exact classical baseline -- `build_benchmark_result` below stays as the
single-shot, no-scoring builder LISS-0323 shipped, unchanged, for callers
that only need the terminal-measurement mapping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from compiler.staqex.host import JobResult


@dataclass(frozen=True)
class BenchmarkResult:
    """Host report for one S02 execution.

    An empty, missing, or unverifiable terminal observation is recorded as
    a `"failed"` feasibility_verdict with no terminal_selection -- never a
    fabricated selection or score.
    """

    feasibility_verdict: str  # "feasible" | "failed"
    terminal_selection: Any | None
    resource_metadata: dict[str, Any] = field(default_factory=dict)
    optimality_claim: str = "none"
    # LISS-0403: populated by benchmark_report.py; None/empty when only the
    # single-shot build_benchmark_result builder below was used.
    baseline_score: float | None = None
    objective_score: float | None = None
    reranked_score: float | None = None
    quality_metrics: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    # LISS-0438: keep exact-local output, finite-target plan evidence, and
    # rejection diagnostics as separate channels.  These fields are additive
    # so existing single-shot callers retain their prior contract.
    exact_local: dict[str, Any] = field(default_factory=dict)
    finite_target: dict[str, Any] = field(default_factory=dict)
    realization_provenance: dict[str, Any] = field(default_factory=dict)
    diagnostic_rejection_evidence: dict[str, Any] | None = None
    target_plan_provenance: dict[str, Any] | None = None
    capability_rejection: str | None = None
    partial_program: Any | None = None


def build_benchmark_result(job_result: JobResult) -> BenchmarkResult:
    """Build a BenchmarkResult from a JobResult's terminal measurement.

    Resource metadata is copied verbatim from the JobResult; nothing is
    invented when the JobResult does not provide it.
    """

    resource_metadata = dict(job_result.metadata)

    if not job_result.measurements:
        return BenchmarkResult(
            feasibility_verdict="failed",
            terminal_selection=None,
            resource_metadata=resource_metadata,
        )

    envelope = job_result.measurements[-1]
    if envelope.vacuum:
        return BenchmarkResult(
            feasibility_verdict="failed",
            terminal_selection=None,
            resource_metadata=resource_metadata,
        )

    return BenchmarkResult(
        feasibility_verdict="feasible",
        terminal_selection=envelope.value,
        resource_metadata=resource_metadata,
    )
