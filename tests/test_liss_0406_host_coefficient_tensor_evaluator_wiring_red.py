"""AT-TDD Phase 1 Red: wire HostInputPort into the Host coefficient
tensor path so `Float[N]... = host("key")` placeholders are reachable
from a real Evaluator run, not only from a hand-built
`lower_finite_binder_operators(host_arrays=...)` call.

Target: docs/issues/LISS-0406-host-coefficient-tensor-evaluator-wiring.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host_input_port import MappingHostInputAdapter  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelError  # noqa: E402


_SOURCE = """
package t
pub fn main() -> Unit {
    Energy scale = 1.0.eV to J
    Float[1] coeff = host("coupling")
    Operator H_raw = Sigma (i In 0..0) { coeff[i] * X[i] }
    Operator H = scale * H_raw
    State q = |0>
    Time dur = 0.6.fs
    State q = Evolve { q under H for dur }.run()
    Measure q
}
"""


def test_host_coupling_reaches_a_real_evaluator_run() -> None:
    """A `host("coupling")`-bound coefficient must actually drive the
    evolution when supplied through a real Evaluator's HostInputPort --
    two different Host-supplied coupling strengths must produce two
    different terminal distributions. Today this raises `KernelError:
    unknown function \\`host\\`` because Evaluator never builds
    `host_arrays` from `self.host_input`, so the sum-binder's `coeff[i]`
    reference is never lowered to a literal and the raw `host(...)` Call
    falls through to generic evaluation, which doesn't know `host()`.
    """
    compiled = compile_source(_SOURCE)
    assert compiled.unit is not None, compiled.diagnostics

    ev_small = Evaluator(seed=0, host_input=MappingHostInputAdapter({"coupling": [0.1]}))
    result_small = ev_small.run_unit(compiled.unit)
    ev_large = Evaluator(seed=0, host_input=MappingHostInputAdapter({"coupling": [5.0]}))
    result_large = ev_large.run_unit(compiled.unit)

    assert result_small.measure is not None
    assert result_large.measure is not None
    assert result_small.measure.marginal != result_large.measure.marginal


def test_missing_host_coefficient_fails_closed_from_a_real_evaluator_run() -> None:
    """A `host("key")` placeholder with no matching HostInputPort entry
    must fail closed with a stable diagnostic code, not a generic
    `unknown function` crash and not a silent zero-substitution.
    """
    compiled = compile_source(_SOURCE)
    assert compiled.unit is not None, compiled.diagnostics

    ev = Evaluator(seed=0, host_input=MappingHostInputAdapter({}))
    raised = None
    try:
        ev.run_unit(compiled.unit)
    except KernelError as exc:
        raised = exc
    assert raised is not None
    assert getattr(raised, "code", None) == "HOST_COEFFICIENT_MISSING", raised


def test_program_without_host_placeholders_is_unaffected() -> None:
    """Regression guard: programs with no `host("key")` coefficient
    placeholders must Evolve exactly as before this wiring change."""
    source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = 1.0 * Z[0] + 1.0 * X[0] + 1.0 * (Z[0] * Z[1])
        Operator H = scale * H_raw
        State q0 = |0>
        State q1 = |+>
        Time dur = 0.6.fs
        State (q0, q1) = Evolve { (q0, q1) under H for dur }.run()
        Measure q0 tracing_out q1
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    import math

    assert math.isclose(result.measure.marginal[0], 0.6078963648762783, rel_tol=1e-9)
    assert math.isclose(result.measure.marginal[1], 0.39210363512372154, rel_tol=1e-9)
