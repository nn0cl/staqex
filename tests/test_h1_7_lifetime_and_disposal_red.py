"""Phase 1 Red tests for H1 lifetime and disposal semantics."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_h1_7_trace_out_is_disposal_not_uncompute() -> None:
    compiled = compile_source(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment dispose() {
          prepare |00>
          Measure probe tracing_out ancilla
        }
        """
    )

    assert not compiled.diagnostics
    assert compiled.state_transform_plan is not None
    trace = next(
        step
        for step in compiled.state_transform_plan.steps
        if step.kind == "TraceOut"
    )
    assert trace.kind != "Uncompute"
    assert "Unitary" not in trace.characteristics
    assert "Adj" not in trace.characteristics


def test_h1_7_uncompute_records_reversible_lifetime_obligation() -> None:
    compiled = compile_source(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment restore() {
          prepare |00>
          uncompute ancilla witness |0>
          Measure
        }
        """
    )

    assert not compiled.diagnostics
    assert compiled.state_transform_plan is not None
    uncompute = next(
        step
        for step in compiled.state_transform_plan.steps
        if step.kind == "Uncompute"
    )
    assert uncompute.kind != "TraceOut"
    assert "Adj" in uncompute.characteristics
    assert compiled.quantum_semantic_ir is not None
    assert compiled.quantum_semantic_ir.uncompute_obligations


def test_h1_7_missing_uncompute_witness_is_rejected() -> None:
    compiled = compile_source(
        """
        theory Ising {
          operator H = Z[0]
        }
        experiment invalid_restore() {
          prepare |00>
          uncompute ancilla
          Measure
        }
        """
    )

    assert "UNCOMPUTE_WITNESS_MISSING" in {
        str(diagnostic.get("code", ""))
        for diagnostic in compiled.diagnostics
    }
    assert compiled.state_transform_plan is None


if __name__ == "__main__":
    test_h1_7_trace_out_is_disposal_not_uncompute()
    test_h1_7_uncompute_records_reversible_lifetime_obligation()
    test_h1_7_missing_uncompute_witness_is_rejected()
    print("OK — H1-7 lifetime and disposal Red tests")
