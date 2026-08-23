#!/usr/bin/env python3
"""Phase 1 Red acceptance tests for LISS-0438.

These tests deliberately describe the residual S02 contract before its
implementation.  They must remain unchanged when the Green implementation is
added: the tests are the reviewed acceptance boundary, not implementation
scaffolding.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[1]
_S02 = _REPO / "examples/showcase/S02_drug_discovery/main_selection.sqx"
_REPORT = _REPO / "examples/showcase/S02_drug_discovery/host/benchmark_report.py"
_BASELINE = (
    _REPO
    / "examples/showcase/S02_drug_discovery/baseline/s02_explicit_evolution_baseline.json"
)


def _source() -> str:
    return _S02.read_text(encoding="utf-8")


def test_exact_local_lane_is_still_source_visible() -> None:
    source = _source()
    for fragment in (
        "State psi_0",
        "P_F",
        "psi_sel",
        "norm",
        "Operator H_obj",
        "Time dur",
        "Measure",
    ):
        assert fragment in source, fragment
    assert "Operator U_t = exp(-i * H_obj * dur / hbar)" in source
    assert "State psi_final = Evolve() { U_t * psi_sel }.run()" in source


def test_target_lane_spells_formal_limit_and_finite_realize() -> None:
    """R3: a finite target plan may not be inferred from exact local Evolve."""

    source = _source()
    assert "Operator U_formal = Limit N -> Infinity" in source
    assert '(I - i * H_obj * dur / (N * hbar)) ^ N' in source
    assert "Operator U_qpu = Realize(" in source
    assert 'source = U_formal' in source
    assert 'method = "suzuki"' in source
    assert "order = 2" in source
    assert "steps = 8" in source
    assert "error_budget = 1e-6" in source


def test_benchmark_report_separates_exact_and_finite_lanes() -> None:
    """R4: comparison output must distinguish local output from target data."""

    report = _REPORT.read_text(encoding="utf-8")
    assert "exact_local" in report
    assert "finite_target" in report
    assert "realization_provenance" in report
    assert "capability_rejection" in report
    assert "diagnostic_rejection_evidence" in report
    assert "target_plan_provenance" in report
    assert "partial_program" in report


def test_pre_migration_baseline_is_frozen_for_phase_1() -> None:
    """R2: Phase 1 records the current source and benchmark identity."""

    expected_source_sha256 = "aa2913616b71945ef4d54fef65eac170b76ea63c4f812642ad2df98b181e3511"
    baseline = json.loads(_BASELINE.read_text(encoding="utf-8"))

    assert baseline["status"] == "pre-migration-reference"
    assert baseline["seed"] == 0
    assert baseline["source_sha256"] == expected_source_sha256
    assert baseline["benchmark_metrics"] == {
        "shots": 20,
        "infeasible_shots": 6,
        "top_k_overlap": 0.33,
        "reproducibility_verified": True,
    }


def test_finite_lane_rejection_keeps_diagnostics_out_of_target_provenance() -> None:
    """R4: unsupported S02 target lowering is diagnostic-only and atomic."""

    host = _REPO / "examples/showcase/S02_drug_discovery/host"
    sys.path.insert(0, str(host))
    try:
        from benchmark_report import _explicit_evolution_comparison

        comparison = _explicit_evolution_comparison()
    finally:
        sys.path.remove(str(host))

    assert comparison["exact_local"]["operator"] == "U_t"
    assert comparison["finite_target"]["operator"] == "U_qpu"
    assert comparison["finite_target"]["submitted"] is False
    assert comparison["finite_target"]["status"] in {
        "realized",
        "capability-rejected",
    }
    if comparison["finite_target"]["status"] == "capability-rejected":
        assert comparison["diagnostic_rejection_evidence"]["code"] == (
            "QASM_TROTTER_UNSUPPORTED_H"
        )
        assert comparison["diagnostic_rejection_evidence"]["target_plan_provenance"] is None
        assert comparison["target_plan_provenance"] is None
    else:
        assert comparison["target_plan_provenance"] is not None
        assert comparison["diagnostic_rejection_evidence"] is None
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
