"""AT-TDD Phase 1 Red: Operator coefficient/binder resolution unification.

Target: docs/architecture/adr/0206-operator-coefficient-resolution-unification.md /
docs/issues/LISS-0407-operator-resolution-unification.md.

Each test targets one of the three confirmed-broken combinations found
while writing S02 (LISS-0402/0405/0406): a Float[N] array threaded
through a function parameter into a sum binder, a struct-field access
hidden behind an intermediate named Operator variable, and a nested
Operator-returning function call inside a larger Operator expression.
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


def test_float_array_param_threaded_into_binder() -> None:
    """A Float[N] array passed as a function parameter, indexed inside
    that function's own `sum` binder body, must resolve -- today this
    raises `cannot compile sparse Pauli for OpBinder` because the
    parameter's array values never reach the binder-lowering pass."""
    source = """
    package t
    fn f(w: Float[2]) -> Operator {
        return sum (i in Index<0..1>) { w[i] * Z[i] }
    }
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Float[2] arr = host("arr")
        Operator H_raw = f(arr)
        Operator H = scale * H_raw
        State q0 = |0>
        State q1 = |0>
        Time dur = 0.6.fs
        State (q0, q1) = evolve { (q0, q1) under H for dur }.run()
        measure q0 tracing_out q1
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics

    ev_small = Evaluator(seed=0, host_input=MappingHostInputAdapter({"arr": [0.1, 0.1]}))
    result_small = ev_small.run_unit(compiled.unit)
    ev_large = Evaluator(seed=0, host_input=MappingHostInputAdapter({"arr": [5.0, 5.0]}))
    result_large = ev_large.run_unit(compiled.unit)

    assert result_small.measure is not None
    assert result_large.measure is not None
    assert result_small.measure.marginal != result_large.measure.marginal


def test_struct_field_indirection_through_named_operator_variable() -> None:
    """A struct-field coefficient bound to an intermediate named Operator
    variable, then combined further, must resolve when that variable is
    later referenced -- today this raises `cannot compile sparse Pauli
    for OpAttr` because materialize_op_attrs does not recurse through a
    bound Operator name."""
    source = """
    package t
    struct W { a: Float }
    pub fn main() -> Unit {
        W weights = W(0.5)
        Operator G = weights.a * Z[0]
        Operator H_raw = G + X[0]
        Energy scale = 1.0.eV to J
        Operator H = scale * H_raw
        State q = |0>
        Time dur = 0.6.fs
        State q = evolve { q under H for dur }.run()
        measure q
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    assert result.measure.vacuum is False


def test_nested_operator_returning_call_inside_larger_expression() -> None:
    """A call to an Operator-returning function used inline inside a
    larger Operator expression (not bound to its own name first) must
    resolve -- today this raises `cannot compile sparse Pauli for
    OpCall` (the LISS-0402-disclosed "Operator-Call-inline" gap)."""
    source = """
    package t
    struct W { a: Float }
    fn f(w: W) -> Operator {
        return w.a * Z[0]
    }
    pub fn main() -> Unit {
        W weights = W(0.5)
        Energy scale = 1.0.eV to J
        Operator H = scale * f(weights)
        State q = |0>
        Time dur = 0.6.fs
        State q = evolve { q under H for dur }.run()
        measure q
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    assert result.measure.vacuum is False


def test_missing_binder_array_fails_closed_with_a_clear_diagnostic() -> None:
    """A binder that genuinely needs Host array data it never received
    must fail with a clear, specific diagnostic -- not a silent pass-
    through to a much later, vaguer `cannot compile sparse Pauli for
    OpBinder` error three frames away."""
    source = """
    package t
    fn f(w: Float[2]) -> Operator {
        return sum (i in Index<0..1>) { w[i] * Z[i] }
    }
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Float[2] arr = host("missing_key")
        Operator H_raw = f(arr)
        Operator H = scale * H_raw
        State q0 = |0>
        State q1 = |0>
        Time dur = 0.6.fs
        State (q0, q1) = evolve { (q0, q1) under H for dur }.run()
        measure q0 tracing_out q1
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    raised = None
    try:
        Evaluator(seed=0, host_input=MappingHostInputAdapter({})).run_unit(compiled.unit)
    except KernelError as exc:
        raised = exc
    assert raised is not None
    assert "OpBinder" not in str(raised), (
        "must not fall through to the generic sparse-Pauli error"
    )
