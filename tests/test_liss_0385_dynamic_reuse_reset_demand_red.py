"""AT-TDD Phase 1 Red: LISS-0385 reuse/reset demand inference (ADR 0199).

Target: docs/specs/staqex-dynamic-qpu-lane.md § reuse/reset demand (LISS-0385).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dynamic_capability import (  # noqa: E402
    infer_dynamic_capability_demand,
)
from compiler.staqex.pipeline import compile_source  # noqa: E402


_SOURCE_MEASURE_ONLY = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        Controller<Bit> bit = measure q
    }
    State<Int> observed = coin()
    measure observed
}
"""

_SOURCE_POST_MEASURE_APPLY = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { apply(X, q) }
            1 => { apply(Z, q) }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""

_SOURCE_WITHIN_MEASURE_ONLY = """
package t
pub fn main() -> Unit {
    dynamic qpu within coherent_window {
        state q = |0>
        Controller<Bit> bit = measure q
    }
    State<Int> observed = coin()
    measure observed
}
"""


def test_mid_circuit_measure_alone_does_not_demand_reuse() -> None:
    """Scenario: mid-circuit measure alone does not demand reuse."""
    compiled = compile_source(_SOURCE_MEASURE_ONLY)
    demand = infer_dynamic_capability_demand(compiled.unit)

    assert demand.needs_reuse is False
    assert demand.needs_reset is False


def test_post_measure_apply_on_measured_wire_demands_reuse() -> None:
    """Scenario: post-measure apply on the measured wire demands reuse."""
    compiled = compile_source(_SOURCE_POST_MEASURE_APPLY)
    demand = infer_dynamic_capability_demand(compiled.unit)

    assert demand.needs_reuse is True
    assert demand.needs_reset is False
    codes = {str(d.get("code", "")) for d in compiled.diagnostics}
    assert "DYN_CAPABILITY_REUSE" in codes or "DYNAMIC_REUSE_UNSUPPORTED" in codes


def test_within_timing_does_not_imply_reuse() -> None:
    """Scenario: within timing does not imply reuse."""
    compiled = compile_source(_SOURCE_WITHIN_MEASURE_ONLY)
    demand = infer_dynamic_capability_demand(compiled.unit)
    timing = [
        r
        for r in (compiled.quantum_semantic_ir.regions if compiled.quantum_semantic_ir else [])
        if type(r).__name__ == "TimingRegion"
    ]

    assert demand.needs_reuse is False
    assert demand.needs_reset is False
    assert len(timing) == 1
    assert timing[0].timing_intent == "coherent_window"
