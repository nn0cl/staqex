#!/usr/bin/env python3
"""Phase 1 Red acceptance tests for LISS-0443.

These tests freeze the numerical-comparison evidence contract before any
implementation or benchmark rerun is changed.  The first scenario is
intentionally Red against the current report: the report has realization
provenance, but does not yet expose the source identity and seed used for the
numeric comparison in its result record.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[1]
_HOST = _REPO / "examples/showcase/S02_drug_discovery/host"
_SOURCE = _REPO / "examples/showcase/S02_drug_discovery/main_selection.sqx"


def _with_host_dir() -> None:
    if str(_HOST) not in sys.path:
        sys.path.insert(0, str(_HOST))


def test_numeric_report_records_source_identity_and_seed() -> None:
    """R1: a numerical result must be reproducible from its evidence record."""

    _with_host_dir()
    from benchmark_report import build_report

    base_seed = 100
    report = build_report(shots=6, base_seed=base_seed)
    expected_source_sha256 = hashlib.sha256(
        _SOURCE.read_bytes()
    ).hexdigest()

    assert report.quality_metrics["source_sha256"] == expected_source_sha256
    assert report.quality_metrics["base_seed"] == base_seed


def test_numeric_report_preserves_the_realization_policy_used() -> None:
    """R2: comparison evidence must expose the policy actually inspected."""

    _with_host_dir()
    from benchmark_report import _explicit_evolution_comparison

    comparison = _explicit_evolution_comparison()
    provenance = comparison["realization_provenance"]

    assert provenance["realization_policy"] == "explicit_realize"
    assert provenance["method"] == "suzuki"
    assert provenance["order"] == 2
    assert provenance["steps"] == 8
    assert provenance["error_budget"] == 1e-6


def test_numeric_report_keeps_rejected_finite_lane_atomic() -> None:
    """R3: capability rejection must not become numerical target evidence."""

    _with_host_dir()
    from benchmark_report import _explicit_evolution_comparison

    comparison = _explicit_evolution_comparison()

    assert comparison["finite_target"]["status"] == "capability-rejected"
    assert comparison["finite_target"]["submitted"] is False
    assert comparison["capability_rejection"] == "QASM_TROTTER_UNSUPPORTED_H"
    assert comparison["target_plan_provenance"] is None
    assert comparison["partial_program"] is None


if __name__ == "__main__":
    import traceback

    failures = 0
    for name, test in sorted(globals().items()):
        if not name.startswith("test_"):
            continue
        try:
            test()
        except Exception:
            failures += 1
            print(f"FAIL: {name}")
            traceback.print_exc()
        else:
            print(f"PASS: {name}")
    raise SystemExit(1 if failures else 0)
