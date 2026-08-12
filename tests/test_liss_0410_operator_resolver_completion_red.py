"""AT-TDD Phase 1 Red: complete the ADR 0206/LISS-0407 unified Operator
resolver so apply/capply (and inline anonymous evolve expressions) see
fully-resolved Operator AST, not just evolve's own named-bind path.

Target: docs/issues/LISS-0410-operator-resolver-completion.md.

Independent-context code review (this session) found LISS-0407's
`_resolve_operator_tree` never actually learned to handle `OpAttr` --
that stayed a separate, bolted-on call only reachable from evolve's own
call site and the factory-call path. `apply`/`capply` read
`self.operators[name]` directly with no resolution step at all.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelError  # noqa: E402


def test_apply_resolves_struct_field_coefficient() -> None:
    """`apply(Bad, psi)` where Bad's coefficient comes from a struct
    field must run -- today it raises `cannot compile operator node
    OpAttr` even though the identical form already works for `evolve`."""
    source = """
    package t
    struct W { a: Float }
    pub fn main() -> Unit {
        W weights = W(1.0)
        Operator U = weights.a * X
        state psi = |0>
        state psi = apply(U, psi)
        measure psi
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    assert result.measure.vacuum is False


def test_apply_resolution_does_not_add_a_new_runtime_unitary_check() -> None:
    """Scope guard, corrected during this Issue's own Red phase: the
    runtime `apply` path has never validated unitarity -- only the
    static `check` command does (`unitarity_check.py`, LISS-0411's own
    scope). Confirmed directly: even a bare-literal non-unitary
    `Operator Bad = 2.0 * X; apply(Bad, psi)` already ran without error
    before this Issue (unnormalized `marginal={1: 4.0}`, not a
    KernelError). This Issue only makes struct-field resolution reach
    `apply`/`capply` at all; it must not silently start rejecting
    (or silently start accepting differently) programs the runtime
    never validated in the first place -- both the literal and the
    struct-field form must behave identically (same unnormalized-result
    shape), matching the shipped pre-Issue baseline."""
    literal_source = """
    package t
    pub fn main() -> Unit {
        Operator Bad = 2.0 * X
        state psi = |0>
        state psi = apply(Bad, psi)
        measure psi
    }
    """
    struct_source = """
    package t
    struct W { a: Float }
    pub fn main() -> Unit {
        W weights = W(2.0)
        Operator Bad = weights.a * X
        state psi = |0>
        state psi = apply(Bad, psi)
        measure psi
    }
    """
    literal_compiled = compile_source(literal_source)
    struct_compiled = compile_source(struct_source)
    assert literal_compiled.unit is not None, literal_compiled.diagnostics
    assert struct_compiled.unit is not None, struct_compiled.diagnostics

    literal_result = Evaluator(seed=0).run_unit(literal_compiled.unit)
    struct_result = Evaluator(seed=0).run_unit(struct_compiled.unit)
    assert literal_result.measure is not None
    assert struct_result.measure is not None
    assert literal_result.measure.marginal == struct_result.measure.marginal


def test_operator_variable_indirection_still_works_via_operators_dict_shortcut() -> None:
    """Regression guard: the `_resolve_operator_expr` early-return
    shortcut for `Operator H = G` (G already a bound Operator name) must
    still return a fully resolved tree once routed through the
    completed resolver, not just the raw stored value."""
    source = """
    package t
    struct W { a: Float }
    pub fn main() -> Unit {
        W weights = W(0.5)
        Operator G = weights.a * Z[0]
        Operator H = G
        state q = |0>
        state q = apply(H, q)
        measure q
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None


def test_inline_compound_evolve_expression_was_never_supported() -> None:
    """Correction found during this Issue's own Red phase: an inline
    *compound* Operator expression at `evolve ... under <expr> for t`
    (never bound to a name) was never a working form at all, with or
    without a struct field -- `evolve q under scale * Z for dur` fails
    the same way as the struct-field case, because the parser produces
    generic `BinOp`/`Attr`/`Var` nodes for this position, not the
    Operator-DSL `Op*` AST `_resolve_operator_tree` operates on. This is
    a separate, pre-existing parser-level gap, not something LISS-0407
    ever fixed or regressed -- out of scope for this Issue. Locked in as
    a regression guard so this doesn't get silently "fixed" by accident
    without a deliberate decision. A *bare* Pauli literal (`under Z`)
    still works inline (unaffected, not exercised by this test)."""
    source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        state q = |0>
        Time dur = 0.6.fs
        state q = evolve q under scale * Z for dur
        measure q
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    raised = None
    try:
        Evaluator(seed=0).run_unit(compiled.unit)
    except KernelError as exc:
        raised = exc
    assert raised is not None
    assert "hamiltonian must be Operator name or Pauli literal" in str(raised)


def test_existing_liss_0407_cases_still_pass() -> None:
    """Regression guard: the three LISS-0407 target cases must remain
    fixed after completing the resolver."""
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
        state q = |0>
        Time dur = 0.6.fs
        state q = evolve q under H for dur
        measure q
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    assert result.measure.vacuum is False
