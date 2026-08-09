"""AT-TDD Phase 1 Red: LISS-0382 mid-circuit measure / feed-forward (ADR 0197).

Target behavior is docs/specs/staqex-dynamic-qpu-lane.md § "Acceptance
scenarios — mid-circuit measure / feed-forward (ADR 0197, LISS-0382)".
Default Plan: QSem witnesses + diagnostics; dynamic-lane capability
rejection retained; no Fake executor wiring.

These tests intentionally describe not-yet-implemented behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(diagnostics: list[dict[str, object]]) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


def _regions_named(compiled, name: str) -> list[object]:
    if compiled.quantum_semantic_ir is None:
        return []
    return [
        region
        for region in compiled.quantum_semantic_ir.regions
        if type(region).__name__ == name
    ]


_SOURCE_MID_CIRCUIT_CONTROLLER = """
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

_SOURCE_STATIC_CONTROLLER_MEASURE = """
package t
pub fn main() -> Unit {
    state q = |0>
    Controller<Bit> bit = measure q
    measure q
}
"""

_SOURCE_OBSERVE = """
package t
pub fn main() -> Unit {
    state x = |0>
    observe x
    measure x
}
"""

_SOURCE_MATCH_FEED_FORWARD = """
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

_SOURCE_WITHIN_AND_MID_CIRCUIT = """
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

_SOURCE_STATIC_TERMINAL = """
package t
pub fn main() -> Unit {
    State<Int> observed = coin()
    measure observed
}
"""


def test_controller_bind_from_measure_inside_dynamic_is_mid_circuit() -> None:
    """Scenario: Controller bind from measure inside dynamic is mid-circuit."""
    compiled = compile_source(_SOURCE_MID_CIRCUIT_CONTROLLER)
    codes = _codes(compiled.diagnostics)
    regions = _regions_named(compiled, "DynamicMeasurementRegion")

    assert "EARLY_COLLAPSE_ERROR" not in codes
    assert len(regions) == 1
    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes


def test_same_controller_measure_outside_dynamic_is_early_collapse() -> None:
    """Scenario: the same Controller = measure form outside dynamic fails as early collapse."""
    compiled = compile_source(_SOURCE_STATIC_CONTROLLER_MEASURE)
    codes = _codes(compiled.diagnostics)

    assert "EARLY_COLLAPSE_ERROR" in codes
    assert _regions_named(compiled, "DynamicMeasurementRegion") == []


def test_observe_remains_retired() -> None:
    """Scenario: observe remains retired."""
    compiled = compile_source(_SOURCE_OBSERVE)
    codes = _codes(compiled.diagnostics)

    assert "RETIRED_KEYWORD" in codes
    assert _regions_named(compiled, "DynamicMeasurementRegion") == []


def test_match_after_mid_circuit_measure_yields_dynamic_control_region() -> None:
    """Scenario: match after mid-circuit measure yields DynamicControlRegion."""
    compiled = compile_source(_SOURCE_MATCH_FEED_FORWARD)
    codes = _codes(compiled.diagnostics)
    measurements = _regions_named(compiled, "DynamicMeasurementRegion")
    controls = _regions_named(compiled, "DynamicControlRegion")

    assert len(measurements) == 1
    assert len(controls) == 1
    assert getattr(controls[0], "measurement_region_id") == getattr(
        measurements[0], "region_id"
    )
    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes


def test_mid_circuit_plus_within_keeps_timing_and_measurement_regions() -> None:
    """Scenario: mid-circuit plus within keeps TimingRegion and DynamicMeasurementRegion."""
    compiled = compile_source(_SOURCE_WITHIN_AND_MID_CIRCUIT)
    codes = _codes(compiled.diagnostics)
    timing = _regions_named(compiled, "TimingRegion")
    measurements = _regions_named(compiled, "DynamicMeasurementRegion")

    assert len(timing) == 1
    assert getattr(timing[0], "timing_intent") == "coherent_window"
    assert len(measurements) == 1
    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes


def test_static_terminal_measure_is_unchanged() -> None:
    """Scenario: Static terminal measure is unchanged."""
    compiled = compile_source(_SOURCE_STATIC_TERMINAL)
    codes = _codes(compiled.diagnostics)

    assert _regions_named(compiled, "DynamicMeasurementRegion") == []
    assert _regions_named(compiled, "DynamicControlRegion") == []
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" not in codes
    assert compiled.ok
