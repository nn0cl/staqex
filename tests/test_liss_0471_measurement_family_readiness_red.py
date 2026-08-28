"""AT-TDD Phase 1 Red: LISS-0471 measurement-family readiness.

The existing Dynamic QPU lane tests prove low-level parsing and IR markers.
This Issue adds the missing readiness-classification contract without
reimplementing that lane or contacting a provider.  The classifier is not
implemented yet, so these tests intentionally remain Red.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _classify(source: str, *, source_id: str):
    from compiler.staqex.measurement_family_readiness import classify_for_qpu

    return classify_for_qpu(source, source_id=source_id)


def test_static_terminal_measurement_is_not_dynamic() -> None:
    source = """
    package static_measurement
    pub fn main() -> Unit {
        State<Int> observed = Coin()
        Measure observed
    }
    """

    decision = _classify(source, source_id="synthetic.static_measurement.sqx")

    assert decision.family == "measurement"
    assert decision.semantic_role == "terminal_measurement"
    assert decision.lane == "terminal_classical"
    assert decision.dynamic_region_count == 0
    assert decision.artifact is None


def test_dynamic_measurement_preserves_dynamic_lane_and_provenance() -> None:
    source_id = "tests/fixtures/semantic_core/dynamic_measurement.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")

    decision = _classify(source, source_id=source_id)

    assert decision.family == "measurement"
    assert decision.semantic_role == "dynamic_measurement_feedback"
    assert decision.lane == "dynamic_measurement"
    assert decision.source_id == source_id
    assert decision.dynamic_region_count == 1
    assert decision.terminal_collapse_substitution is False


def test_unsupported_dynamic_target_rejects_before_artifact_or_qasm() -> None:
    source_id = "tests/fixtures/semantic_core/dynamic_measurement.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")

    decision = _classify(source, source_id=source_id)

    assert decision.status == "rejected"
    assert decision.diagnostics == (
        "DYNAMIC_CAPABILITY_REQUIRED_ERROR",
        "DYNAMIC_UNSUPPORTED_FEATURE_ERROR",
    )
    assert decision.artifact is None
    assert decision.qasm is None


def test_povm_and_tomography_are_explicitly_deferred() -> None:
    with pytest.raises(ValueError, match="measurement realization deferred"):
        _classify(
            "POVM tomography measurement",
            source_id="synthetic.povm_tomography.sqx",
        )
