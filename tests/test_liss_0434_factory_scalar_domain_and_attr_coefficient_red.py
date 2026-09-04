"""AT-TDD Phase 1 Red -> Green: an `Operator`-returning factory function's
own scalar parameter can bound a `Sigma`/`Pi` binder's own `Index` range
(e.g. `Sigma (i In 0..n-1)` where `n` is the factory's own parameter, not
a module-level constant), and a struct-attr parameter (`w.activity`) can
appear as the binder's own per-term coefficient alongside an indexed
array coefficient, not only as a post-hoc scale of an already-built
Operator.

Target: docs/issues/LISS-0434-factory-scalar-domain-and-attr-coefficient.md.
Found while reviewing S02's `objective_hamiltonian` (main_selection.sqx)
against its own blackboard equation: it hardcoded `0..7`/`Float[8]`
disconnected from step 1/2's own `n`, and pulled `w.activity` etc. out of
each Sigma as a post-hoc scale instead of writing it as the Sigma's own
per-term coefficient (mathematically equivalent by distributivity, but
not a literal transcription).
"""

from __future__ import annotations

from canonical_execution import run_canonical

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.hamiltonian import compile_hamiltonian  # noqa: E402


def _run(src: str):
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    return run_canonical(compiled, Evaluator(seed=0))


def test_factory_scalar_param_bounds_sigma_index_domain() -> None:
    """`Sigma (i In 0..n-1)` where `n` is the factory's own Int
    parameter (not a module-level constant) -- previously crashed with
    `cannot lower Operator binder: static Index endpoint 'n' is not a
    binder or register size` because the eager first-pass resolution in
    `_resolve_operator_factory_call` tried to lower the binder's domain
    before the call's own scalar params were folded into it."""
    src = """
    package t
    fn f(n: Int, activity_w: Float[3]) -> Operator {
        Operator z_field = Sigma (i In 0..n-1) { activity_w[i] * Z[i] }
        return z_field
    }
    pub fn main() -> Unit {
        Float[3] a = [1.0, 2.0, 3.0]
        Int n = 3
        Operator H = f(n, a)
        Measure |0>
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    run_canonical(compiled, evaluator)
    matrix = compile_hamiltonian(evaluator.operators["H"], env={}, n_qubits=3)
    diag = [matrix[i][i].real for i in range(8)]
    for idx in range(8):
        bits = [(idx >> (2 - k)) & 1 for k in range(3)]
        expected = sum(
            (1.0 if b == 0 else -1.0) * w for b, w in zip(bits, [1.0, 2.0, 3.0])
        )
        assert abs(diag[idx] - expected) < 1e-9


def test_factory_scalar_param_bounds_two_index_sigma_with_guard() -> None:
    """The same, for a two-binder `Sigma (i In 0..n-1, j In 0..n-1) where
    i < j` -- the shape `objective_hamiltonian`'s own coupling term uses."""
    src = """
    package t
    fn f(n: Int) -> Operator {
        Operator coupling = Sigma (i In 0..n-1, j In 0..n-1) where i < j {
            Z[i] * Z[j]
        }
        return coupling
    }
    pub fn main() -> Unit {
        Int n = 3
        Operator H = f(n)
        Measure |0>
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    run_canonical(compiled, evaluator)
    matrix = compile_hamiltonian(evaluator.operators["H"], env={}, n_qubits=3)
    diag = [matrix[i][i].real for i in range(8)]
    for idx in range(8):
        bits = [(idx >> (2 - k)) & 1 for k in range(3)]
        spins = [1.0 if b == 0 else -1.0 for b in bits]
        expected = spins[0] * spins[1] + spins[0] * spins[2] + spins[1] * spins[2]
        assert abs(diag[idx] - expected) < 1e-9


def test_struct_attr_as_sigma_per_term_coefficient() -> None:
    """`w.activity * activity_w[i] * Z[i]` -- a struct-field parameter as
    part of the Sigma's own per-term coefficient product, alongside an
    indexed array coefficient, combined with the scalar-domain case above
    in one factory call (the exact target shape `objective_hamiltonian`
    needs) -- previously crashed with `binder body is outside the
    accepted Pauli slice` because the eager first pass saw a raw,
    unresolved `OpAttr` where only a literal/array-indexed/scalar-var
    coefficient was accepted."""
    src = """
    package t
    struct ObjectiveWeights {
        activity: Float,
        selectivity: Float,
        diversity: Float
    }
    fn objective_hamiltonian(w: ObjectiveWeights, n: Int, activity_w: Float[3], selectivity_w: Float[3]) -> Operator {
        Operator z_field = Sigma (i In 0..n-1) { w.activity * activity_w[i] * Z[i] }
        Operator x_field = Sigma (i In 0..n-1) { w.selectivity * selectivity_w[i] * X[i] }
        Operator coupling = Sigma (i In 0..n-1, j In 0..n-1) where i < j {
            w.diversity * Z[i] * Z[j]
        }
        return z_field + x_field + coupling
    }
    pub fn main() -> Unit {
        Float[3] a = [1.0, 2.0, 3.0]
        Float[3] s = [0.5, 0.5, 0.5]
        Int n = 3
        ObjectiveWeights weights = ObjectiveWeights { activity: 2.0, selectivity: 1.0, diversity: 1.0 }
        Operator H = objective_hamiltonian(weights, n, a, s)
        Measure |0>
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    run_canonical(compiled, evaluator)
    matrix = compile_hamiltonian(evaluator.operators["H"], env={}, n_qubits=3)
    diag = [matrix[i][i].real for i in range(8)]
    for idx in range(8):
        bits = [(idx >> (2 - k)) & 1 for k in range(3)]
        spins = [1.0 if b == 0 else -1.0 for b in bits]
        z_part = sum(
            2.0 * aw * sp for aw, sp in zip([1.0, 2.0, 3.0], spins)
        )
        coupling = spins[0] * spins[1] + spins[0] * spins[2] + spins[1] * spins[2]
        expected = z_part + 1.0 * coupling
        assert abs(diag[idx] - expected) < 1e-9


def test_main_selection_objective_hamiltonian_still_matches_hardcoded_baseline() -> None:
    """S02's own `objective_hamiltonian`, rewritten to use `n`/per-term
    `w.*` coefficients (LISS-0434), reproduces the exact same terminal
    selection at seed 0 as the pre-rewrite hardcoded-`0..7` version
    (`(0, 1, 1, 1, 1, 1, 0, 0)`, matching the pre-batch baseline LISS-0433
    already confirmed) -- since the rewrite is a literal, distributivity-
    equivalent transcription, not a physics change."""
    from pathlib import Path as _Path

    sqx = (
        _Path(__file__).resolve().parents[1]
        / "examples"
        / "showcase"
        / "S02_drug_discovery"
        / "main_selection.sqx"
    )
    host_dir = sqx.parent / "host"
    sys.path.insert(0, str(host_dir))
    try:
        from run_selection import build_objective_weight_arrays, build_predicate_matrices
    finally:
        sys.path.remove(str(host_dir))
    from compiler.staqex.pipeline import compile_path
    from compiler.staqex.host_input_port import MappingHostInputAdapter

    compiled = compile_path(str(sqx))
    assert compiled.unit is not None, compiled.diagnostics
    pairwise, diversity = build_predicate_matrices()
    activity_w, selectivity_w = build_objective_weight_arrays()
    host_input = MappingHostInputAdapter(
        {
            "pairwise_compatible": pairwise,
            "diversity": diversity,
            "activity_weights": activity_w,
            "selectivity_weights": selectivity_w,
        }
    )
    result = run_canonical(compiled, Evaluator(seed=0, host_input=host_input))
    assert result.measure.vacuum is False
    assert result.measure.value == (0, 1, 1, 1, 1, 1, 0, 0)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0434 Green")
