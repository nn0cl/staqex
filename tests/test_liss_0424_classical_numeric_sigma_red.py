"""AT-TDD Phase 1 Red -> Green: classical numeric `Sigma`/`Pi` -- a third
result-kind for the `Sigma`/`Pi` keyword alongside the existing
Operator-typed and State-typed (`KetSumBinder`) forms.

Target: docs/issues/LISS-0424-classical-numeric-sigma.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def _run(src: str):
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    return Evaluator(seed=0).run_unit(compiled.unit)


def test_bare_classical_sigma_sums_the_index() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int total = Sigma (i In 0..2) { i }
        Measure total
    }
    """
    result = _run(src)
    assert result.measure.value == 3  # 0+1+2


def test_classical_pi_multiplies() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int total = Pi (i In 1..3) { i }
        Measure total
    }
    """
    result = _run(src)
    assert result.measure.value == 6  # 1*2*3


def test_classical_sigma_indexes_a_tuple_valued_state_coordinate() -> None:
    """The target shape for S02's step 2 `F` predicate: `x[i]` where `x`
    is a tuple-valued State coordinate, summed classically to a count."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        State x = prepare_selection(3)
        Bool exactly_two = Sigma (i In 0..n-1) { x[i] } == 2
        Measure exactly_two
        Measure x
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None
    # C(3,2) = 3 of the 8 equally-weighted 3-bit patterns have exactly two
    # 1-bits.
    assert abs(result.measure.marginal.get(True, 0.0) - 3 / 8) < 1e-9
    assert abs(result.measure.marginal.get(False, 0.0) - 5 / 8) < 1e-9


def test_multi_binding_classical_sigma_with_guard_recurses_correctly() -> None:
    """`Sigma (i In D1, j In D2) where i < j { x[i] * x[j] }` -- the
    nested-OpBinder nesting the parser already produces for multi-binding
    must fold correctly in the classical path too, not just the Operator
    path."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        State x = prepare_selection(3)
        Int pair_count = Sigma (i In 0..n-1, j In 0..n-1) where i < j { x[i] * x[j] }
        Measure pair_count
        Measure x
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    marg = result.measure.marginal
    # 000/001/010/100 -> 0 selected-pairs (4/8); 011/101/110 -> 1 (3/8);
    # 111 -> 3 (1/8). Hand-computed, not guessed.
    assert abs(marg.get(0, 0.0) - 4 / 8) < 1e-9
    assert abs(marg.get(1, 0.0) - 3 / 8) < 1e-9
    assert abs(marg.get(3, 0.0) - 1 / 8) < 1e-9


def test_classical_sigma_rejects_pauli_atom_in_body() -> None:
    """A Pauli/Operator atom inside a classically-evaluated Sigma body is
    a clear runtime error, not silent misinterpretation -- Operator-typed
    Sigma reaches a completely different code path (never `_bind`), so
    this only fires if something is genuinely miswired."""
    src = """
    package t
    pub fn main() -> Unit {
        Int total = Sigma (i In 0..1) { Z[i] }
        Measure total
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    try:
        Evaluator(seed=0).run_unit(compiled.unit)
        raise AssertionError("expected KernelError for Pauli atom in classical Sigma")
    except Exception as e:  # noqa: BLE001
        assert "non-classical" in str(e)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0424 Slice B Phase 2 Green")
