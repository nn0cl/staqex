"""AT-TDD Phase 1 Red: LISS-0389 dynamic_trace physical outcome confirmation.

Target: docs/architecture/adr/0198-dynamic-jobresult-composition.md
(Amendment, physical outcome confirmation) / LISS-0389.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import submit_source  # noqa: E402


_SOURCE_MEASURE_ONLY = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { }
            1 => { }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""


def test_consistent_supplied_outcome_is_confirmed() -> None:
    """Scenario: consistent supplied outcome is confirmed."""
    job = submit_source(
        _SOURCE_MEASURE_ONLY,
        settings={
            "dynamic_fake_profile": "SIM0_EXACT",
            "dynamic_supplied_outcomes": {"bit": "0"},
        },
    )
    result = job.result()

    assert result.status == "succeeded"
    assert result.dynamic_trace is not None
    assert result.dynamic_trace.physical_outcome_confirmed is True


def test_inconsistent_supplied_outcome_is_not_confirmed() -> None:
    """Scenario: inconsistent supplied outcome is not confirmed.

    q is prepared |0>; supplying outcome "1" is physically impossible
    (zero Born-rule probability). The run legitimately vacuums (not a
    defect -- JobResult.status stays "succeeded"), but dynamic_trace must
    honestly say the reported controller binding was never confirmed.
    """
    job = submit_source(
        _SOURCE_MEASURE_ONLY,
        settings={
            "dynamic_fake_profile": "SIM0_EXACT",
            "dynamic_supplied_outcomes": {"bit": "1"},
        },
    )
    result = job.result()

    assert result.status == "succeeded"
    assert result.dynamic_trace is not None
    assert result.dynamic_trace.controller_bindings.get("bit") == "1"
    assert result.dynamic_trace.physical_outcome_confirmed is False
