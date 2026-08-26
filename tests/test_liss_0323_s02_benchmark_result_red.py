"""AT-TDD Phase 1 Red: LISS-0323 S02 observation matrix and BenchmarkResult.

Target behavior is docs/specs/staqex-v1-s02-drug-discovery-benchmark.md's
"Acceptance scenarios -- terminal observation and resource reporting"
(work unit D). Host-side only; no Kernel/.sqx change. Tests build
synthetic JobResult/MeasurementEnvelope objects directly, following the
established pattern in tests/test_s01_tonight_ticket_export.py, since no
S02 .sqx program exists yet to produce a real one.

These tests intentionally describe the not-yet-implemented module. They
must fail (ImportError) against the current repo, which has no
examples/showcase/S02_drug_discovery/host/benchmark_result.py yet.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_HOST = _REPO / "examples/showcase/S02_drug_discovery/host"
if str(_HOST) not in sys.path:
    sys.path.insert(0, str(_HOST))

from compiler.staqex.host import JobResult, MeasurementEnvelope  # noqa: E402

from benchmark_result import BenchmarkResult, build_benchmark_result  # noqa: E402


def test_vacuum_terminal_observation_is_a_failed_result() -> None:
    job_result = JobResult(
        status="succeeded",
        measurements=(
            MeasurementEnvelope(
                value=None, marginal={}, vacuum=True, sink=None, output=""
            ),
        ),
    )

    result = build_benchmark_result(job_result)

    assert result.feasibility_verdict == "failed"
    assert result.terminal_selection is None


def test_missing_terminal_observation_is_a_failed_result() -> None:
    job_result = JobResult(status="failed", measurements=())

    result = build_benchmark_result(job_result)

    assert result.feasibility_verdict == "failed"
    assert result.terminal_selection is None


def test_valid_terminal_observation_produces_a_real_verdict() -> None:
    job_result = JobResult(
        status="succeeded",
        measurements=(
            MeasurementEnvelope(
                value="C03",
                marginal={"C03": 1.0},
                vacuum=False,
                sink=None,
                output="",
            ),
        ),
    )

    result = build_benchmark_result(job_result)

    assert result.feasibility_verdict == "feasible"
    assert result.terminal_selection == "C03"


def test_resource_metadata_is_passed_through_not_fabricated() -> None:
    job_result = JobResult(
        status="succeeded",
        measurements=(
            MeasurementEnvelope(
                value="C03", marginal={}, vacuum=False, sink=None, output=""
            ),
        ),
        metadata={"logical_qubits": 4, "target": "local"},
    )

    result = build_benchmark_result(job_result)

    assert result.resource_metadata == {"logical_qubits": 4, "target": "local"}


def test_no_resource_metadata_is_invented_when_absent() -> None:
    job_result = JobResult(
        status="succeeded",
        measurements=(
            MeasurementEnvelope(
                value="C03", marginal={}, vacuum=False, sink=None, output=""
            ),
        ),
    )

    result = build_benchmark_result(job_result)

    assert result.resource_metadata == {}


def test_default_optimality_claim_is_none() -> None:
    job_result = JobResult(
        status="succeeded",
        measurements=(
            MeasurementEnvelope(
                value="C03", marginal={}, vacuum=False, sink=None, output=""
            ),
        ),
    )

    result = build_benchmark_result(job_result)

    assert result.optimality_claim == "none"


if __name__ == "__main__":
    test_vacuum_terminal_observation_is_a_failed_result()
    test_missing_terminal_observation_is_a_failed_result()
    test_valid_terminal_observation_produces_a_real_verdict()
    test_resource_metadata_is_passed_through_not_fabricated()
    test_no_resource_metadata_is_invented_when_absent()
    test_default_optimality_claim_is_none()
    print("GREEN — S02 observation matrix and BenchmarkResult")
