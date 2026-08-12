"""AT-TDD Phase 1 Red: class-method-local and library-fn-local `Operator`
binds skip resolution entirely.

Target: docs/issues/LISS-0413-method-fn-local-operator-resolution.md.

A second independent-context review pass (after LISS-0410/0411/0412)
found two more consumers with the same shape as LISS-0410's original
finding: `Evaluator._bind_method` (runtime/evaluator.py) and
`_bind_user_fun` both store a *local* `Operator` StateBind's raw AST
(`self.operators[stmt.names[0]] = stmt.expr`) with no call to
`_resolve_operator_expr` at all -- unlike the top-level bind dispatch
(line ~484) and the Operator-typed *parameter* binding in
`_bind_user_fun` itself (line ~4094), both of which already resolve.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelError  # noqa: E402


def test_class_method_local_operator_resolves_struct_field() -> None:
    """A struct-field coefficient in a class method's own local
    `Operator` bind must resolve -- today it raises `cannot compile
    operator node OpAttr` even though the identical module-level struct
    read already works fine in `main`."""
    source = """
    package t
    struct W { a: Float }
    class Lat {
      fn init() {}
      pub fn use_op() -> State<Qubit> {
        Operator H = weights.a * X
        State psi = |0>
        State out = apply(H, psi)
        return out
      }
    }
    pub fn main() -> Unit {
      W weights = W(1.0)
      Lat L = Lat()
      State result = L.use_op()
      Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    assert result.measure.vacuum is False


def test_library_fn_local_operator_resolves_struct_field() -> None:
    """Same gap, library `fn` instead of a class method -- today it
    also raises `cannot compile operator node OpAttr`."""
    source = """
    package t
    struct W { a: Float }
    fn use_op() -> State<Qubit> {
        Operator H = weights.a * X
        State psi = |0>
        State out = apply(H, psi)
        return out
    }
    pub fn main() -> Unit {
        W weights = W(1.0)
        State result = use_op()
        Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    assert result.measure.vacuum is False


def test_class_method_local_operator_matches_equivalent_literal_value() -> None:
    """Correctness guard: a struct field holding 2.0 must produce the
    identical result as the equivalent literal `2.0` form -- the
    coefficient must actually reach the Operator, not be silently
    dropped or defaulted."""
    struct_source = """
    package t
    struct W { a: Float }
    class Lat {
      fn init() {}
      pub fn use_op() -> State<Qubit> {
        Operator H = weights.a * X
        State psi = |0>
        State out = apply(H, psi)
        return out
      }
    }
    pub fn main() -> Unit {
      W weights = W(2.0)
      Lat L = Lat()
      State result = L.use_op()
      Measure result
    }
    """
    literal_source = """
    package t
    class Lat {
      fn init() {}
      pub fn use_op() -> State<Qubit> {
        Operator H = 2.0 * X
        State psi = |0>
        State out = apply(H, psi)
        return out
      }
    }
    pub fn main() -> Unit {
      Lat L = Lat()
      State result = L.use_op()
      Measure result
    }
    """
    struct_compiled = compile_source(struct_source)
    literal_compiled = compile_source(literal_source)
    assert struct_compiled.unit is not None, struct_compiled.diagnostics
    assert literal_compiled.unit is not None, literal_compiled.diagnostics

    struct_result = Evaluator(seed=0).run_unit(struct_compiled.unit)
    literal_result = Evaluator(seed=0).run_unit(literal_compiled.unit)
    assert struct_result.measure is not None
    assert literal_result.measure is not None
    assert struct_result.measure.marginal == literal_result.measure.marginal


def test_class_method_local_operator_with_literal_coefficient_still_works() -> None:
    """Regression guard: the already-working literal-coefficient form
    inside a class method must remain unaffected."""
    source = """
    package t
    class Lat {
      fn init() {}
      pub fn use_op() -> State<Qubit> {
        Operator H = 2.0 * X
        State psi = |0>
        State out = apply(H, psi)
        return out
      }
    }
    pub fn main() -> Unit {
      Lat L = Lat()
      State result = L.use_op()
      Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
