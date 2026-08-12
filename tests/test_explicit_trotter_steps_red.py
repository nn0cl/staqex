"""AT-TDD Phase 1 Red: LISS-0050 explicit Trotter step policy (ADR 0094).

Reproduces the gap recorded in
docs/issues/LISS-0050-trotter-step-silent-clamp.md: `backend/qasm/trotter.py`
silently clamped the Trotter step count to 64 with no diagnostic, both for
the derived (`ceil(|t|*8)`) default and for an explicit caller `steps=`
value. Per the Adjudicator's decision (2026-07-25, ADR 0094): QASM emission
of a plain `evolve { ... under H for t }.run()` (no `using Suzuki(...)`
policy) must be rejected with an explicit diagnostic naming the fix; the
already-shipped
`using Suzuki(...)` mechanism (LISS-0017/ADR 0084) is the only path, and it
must never clamp an explicit `steps=` value, however large.

Expected to fail until Phase 2 Green implements the rejection and removes
the silently-clamped functions.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402

_DIAGNOSTIC_CODE = "QASM_TROTTER_STEPS_REQUIRED"

_PLAIN_EVOLVE = """
package t
pub fn main() -> Unit {
    Operator H = 5.272859e-20 * I - 5.272859e-20 * Z[0]
    State psi = |+>
    State psi = evolve { psi under H for 100.0.fs }.run()
    measure psi
}
"""

_EXPLICIT_STEPS_ABOVE_OLD_CAP = """
package t
pub fn main() -> Unit {
    Operator H = 0.5 * I - 0.5 * Z[0]
    State psi = |+>
    State psi = evolve { psi under H for 100.0 using Suzuki(order = 2, steps = 200) }.run()
    measure psi
}
"""


def _emit(source: str):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    return QASM3Emitter(route=False).emit_unit(compiled.unit)


def test_plain_evolve_qasm_emission_is_rejected_not_silently_clamped() -> None:
    emitted = _emit(_PLAIN_EVOLVE)

    assert emitted.ok is False
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == _DIAGNOSTIC_CODE


def test_plain_evolve_rejection_names_the_fix() -> None:
    emitted = _emit(_PLAIN_EVOLVE)

    joined_notes = " ".join(emitted.notes)
    assert "using Suzuki" in joined_notes
    assert "steps" in joined_notes
    assert "tolerance" in joined_notes


def test_plain_evolve_still_runs_on_the_sv_simulator() -> None:
    """The defect and its fix are QASM-lowering-only; expm_ih-based SV
    execution never used Trotter step counts and must be unaffected."""
    result = run_source(_PLAIN_EVOLVE, settings={"target": "local", "seed": 7}, stdout=io.StringIO())

    assert result.status == "succeeded", result.diagnostics


def test_explicit_steps_above_the_old_64_cap_are_honored_exactly() -> None:
    emitted = _emit(_EXPLICIT_STEPS_ABOVE_OLD_CAP)

    assert emitted.ok, emitted.notes
    assert "suzuki S2 step 1/200" in emitted.qasm


def test_explicit_steps_are_never_silently_clamped_even_at_the_old_default() -> None:
    """A small explicit request must also be honored exactly -- this pins
    the case that was already broken before ADR 0094 (an explicit `steps=`
    below 64 worked, but the clamp still applied above it)."""
    small = _emit(
        """
        package t
        pub fn main() -> Unit {
            Operator H = 0.5 * I - 0.5 * Z[0]
            State psi = |+>
            State psi = evolve { psi under H for 1.0 using Suzuki(order = 2, steps = 3) }.run()
            measure psi
        }
        """
    )
    assert small.ok, small.notes
    assert "suzuki S2 step 1/3" in small.qasm


if __name__ == "__main__":
    tests = [
        test_plain_evolve_qasm_emission_is_rejected_not_silently_clamped,
        test_plain_evolve_rejection_names_the_fix,
        test_plain_evolve_still_runs_on_the_sv_simulator,
        test_explicit_steps_above_the_old_64_cap_are_honored_exactly,
        test_explicit_steps_are_never_silently_clamped_even_at_the_old_default,
    ]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:  # noqa: BLE001 -- Red run report, not production code
            failed += 1
            print(f"RED (expected): {test.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed (Red until Phase 2 Green)")
