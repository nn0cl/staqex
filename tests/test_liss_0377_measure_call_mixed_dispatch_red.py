"""AT-TDD: LISS-0377 -- Measure of a DensityState-returning Call
matches the named-Var POVM/mixed path (was silently empty / skipped
domain check).

Design decision: docs/issues/LISS-0377-Measure-call-mixed-dispatch.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _codes(result) -> set[str]:
    return {diagnostic.get("code") for diagnostic in result.diagnostics}


_VAR_MATCH = """
package t
pub fn main() -> Unit {
    DensityState<Qubit> rho = DensityState(
        RawMatrix([[0.25, 0.0], [0.0, 0.75]])
    )
    POVM<Qubit> z = ComputationalBasis()
    Measure rho with z
}
"""

_CALL_MATCH = """
package t
fn make() -> DensityState<Qubit> {
    return DensityState(RawMatrix([[0.25, 0.0], [0.0, 0.75]]))
}
pub fn main() -> Unit {
    POVM<Qubit> z = ComputationalBasis()
    Measure make() with z
}
"""

_VAR_MISMATCH = """
package t
pub fn main() -> Unit {
    DensityState<Qubit> rho = DensityState(
        RawMatrix([[1.0, 0.0], [0.0, 0.0]])
    )
    POVM<Position> p = ComputationalBasis()
    Measure rho with p
}
"""

_CALL_MISMATCH = """
package t
fn make() -> DensityState<Qubit> {
    return DensityState(RawMatrix([[1.0, 0.0], [0.0, 0.0]]))
}
pub fn main() -> Unit {
    POVM<Position> p = ComputationalBasis()
    Measure make() with p
}
"""


def test_named_density_measure_remains_correct() -> None:
    """Regression guard: named DensityState + matching POVM still works."""
    result = run_source(_VAR_MATCH)
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == {0: 0.25, 1: 0.75}
    assert result.metadata.get("state_type") == "DensityState"


def test_call_density_measure_matches_named_path() -> None:
    """A zero-arg Call returning DensityState must Measure like the Var path,
    not succeed with an empty marginal."""
    result = run_source(_CALL_MATCH)
    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == {0: 0.25, 1: 0.75}
    assert result.metadata.get("state_type") == "DensityState"


def test_named_domain_mismatch_remains_rejected() -> None:
    """Regression guard: named DensityState + mismatched POVM still fails."""
    result = run_source(_VAR_MISMATCH)
    assert result.status == "failed"
    assert "POVM_DOMAIN_MISMATCH" in _codes(result)


def test_call_domain_mismatch_is_rejected_the_same_way() -> None:
    """The identical domain mismatch via a Call target must raise
    POVM_DOMAIN_MISMATCH, not silently succeed."""
    result = run_source(_CALL_MISMATCH)
    assert result.status == "failed"
    assert "POVM_DOMAIN_MISMATCH" in _codes(result)
