"""AT-TDD Phase 1 Red -> Green: `Evolve (vars) times N { block }`'s block
must be built only from State arithmetic/tensor-products and calls to an
already-unitarity-checked primitive, or a user function whose own body
satisfies the same constraint recursively -- an opaque call whose own
unitarity is unverified fails closed with `EVOLVE_BLOCK_OPAQUE_TRANSFORM`.

Target: docs/issues/LISS-0436-evolve-times-block-transparency.md.

Found during a direct Adjudicator-driven critical review of `Evolve`'s
design: `unitarity_check.py`'s own docstring already admits "Full proof
of every pushforward remains Deferred" -- the `under H for dur` form gets
a real Hermiticity check, but the `times N { block }` form previously had
*no* check on its own block content at all (it fell through to the
generic child-expression walk, which only finds nested checkable sites,
never asks whether the block itself is trustworthy).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_path, compile_source  # noqa: E402


def _codes(src: str) -> set[str]:
    return {str(d.get("code", "")) for d in compile_source(src).diagnostics}


def test_pure_arithmetic_block_is_transparent() -> None:
    """B06's own shape: no function calls at all, just State arithmetic."""
    src = """
    package t
    pub fn main() -> Unit {
        State<Time> dt = Dirac(0.5.s)
        State<Mass> m = Dirac(1.0.kg)
        State<Stiffness> k = Dirac(1.0.N_m)
        State<Length> x = Dirac(0.0.m)
        State<Momentum> p = Dirac(0.0.kg_m_s)
        State (x, p) = Evolve (x, p) times 2 {
            (x + (dt / m) * p, p - (dt * k) * x)
        }
        Measure x tracing_out dt, m, k, p
    }
    """
    assert "EVOLVE_BLOCK_OPAQUE_TRANSFORM" not in _codes(src)


def test_closed_vocabulary_call_is_transparent() -> None:
    """A direct call to a closed-vocabulary primitive (apply) is allowed."""
    src = """
    package t
    pub fn main() -> Unit {
        Operator H = X
        State c = |0>
        State c = Evolve (c) times 2 {
            apply(H, c)
        }
        Measure c
    }
    """
    assert "EVOLVE_BLOCK_OPAQUE_TRANSFORM" not in _codes(src)


def test_user_function_built_from_closed_vocabulary_is_transparent() -> None:
    """A user-defined function whose own body is built only from
    apply/walk_shift/tensor-products is transparent, recursively --
    the exact shape B09/A02's real (post-LISS-0435) DTQW step uses."""
    src = """
    package t
    fn step(operator: Operator, c: State<Qubit>, x: State<Position>) -> State<(Qubit, Position)> {
        State c2 = apply(operator, c)
        State x2 = walk_shift(c2, x)
        return c2 *|* x2
    }
    pub fn main() -> Unit {
        Operator walk_operator = (X + Z) * 0.7071067811865476
        State c = |0>
        State x = Dirac(0)
        State (c, x) = c *|* x
        State (c, x) = Evolve (c, x) times 2 {
            step(walk_operator, c, x)
        }
        Measure x
    }
    """
    assert "EVOLVE_BLOCK_OPAQUE_TRANSFORM" not in _codes(src)


def test_user_function_building_its_own_operator_locally_is_transparent() -> None:
    """Real, previously-found bug: a function that builds its OWN Operator
    locally (`Operator CoinOp = 0.7071067811865476 * (X + Z)`) before
    `apply`ing it was wrongly flagged opaque -- the Operator-DSL Pauli-atom
    expression (OpBin/OpVar, a different AST family from the general
    expression grammar) isn't a State transform itself and must be
    skipped, matching how `check_unitarity`'s own top-level loop already
    treats Operator binds. `_check_apply_unitary` independently verifies
    the matrix itself is unitary at the `apply` call site."""
    src = """
    package t
    pub fn step(c: State<Qubit>, x: State<Position>) -> State<(Qubit, Position)> {
        Operator CoinOp = 0.7071067811865476 * (X + Z)
        State<Qubit> c = apply(CoinOp, c)
        State<Position> x = walk_shift(c, x)
        return c *|* x
    }
    pub fn main() -> Unit {
        State<Qubit> c = |+>
        State<Position> x = Dirac(0)
        State<(Qubit, Position)> (c, x) = c *|* x
        State (c, x) = Evolve (c, x) times 2 {
            step(c, x)
        }
        Measure x tracing_out c
    }
    """
    assert "EVOLVE_BLOCK_OPAQUE_TRANSFORM" not in _codes(src)


def test_unrecognized_callee_is_opaque() -> None:
    """A call to an undefined/unrecognized name inside the block fails
    closed -- nothing here proves it denotes a coherent transform."""
    src = """
    package t
    pub fn main() -> Unit {
        State c = |0>
        State c = Evolve (c) times 2 {
            some_undefined_black_box(c)
        }
        Measure c
    }
    """
    assert "EVOLVE_BLOCK_OPAQUE_TRANSFORM" in _codes(src)


def test_mix_inside_times_block_is_opaque() -> None:
    """Classical-flavored control flow (`Mix`) inside the block is not on
    the allowlist -- fails closed rather than assuming it's coherent."""
    src = """
    package t
    pub fn main() -> Unit {
        State bit = Coin()
        State c = |0>
        State c = Evolve (c) times 2 {
            Mix (bit) { 0 -> c, else -> c }
        }
        Measure c
    }
    """
    assert "EVOLVE_BLOCK_OPAQUE_TRANSFORM" in _codes(src)


def test_user_function_calling_opaque_callee_is_transitively_opaque() -> None:
    """The recursive check follows one level of user-fn indirection: a
    function that itself calls an unrecognized callee is opaque too, not
    just a direct call site."""
    src = """
    package t
    fn wrapper(c: State<Qubit>) -> State<Qubit> {
        return some_undefined_black_box(c)
    }
    pub fn main() -> Unit {
        State c = |0>
        State c = Evolve (c) times 2 {
            wrapper(c)
        }
        Measure c
    }
    """
    assert "EVOLVE_BLOCK_OPAQUE_TRANSFORM" in _codes(src)


def test_under_hamiltonian_form_is_unaffected() -> None:
    """The `under H for dur` form has its own, pre-existing Hermiticity
    check (unchanged by this Issue) and must not trip the new
    times-block-specific diagnostic at all."""
    src = """
    package t
    pub fn main() -> Unit {
        Operator H = X
        State psi = |0>
        State psi = Evolve { psi under H for 1.0.s }.run()
        Measure psi
    }
    """
    assert "EVOLVE_BLOCK_OPAQUE_TRANSFORM" not in _codes(src)


def test_b06_b09_a02_examples_stay_clean() -> None:
    """The full shipped corpus's only three `times N` usages (B06, B09,
    A02 -- post-LISS-0435's real DTQW step) all compile with no new
    diagnostic."""
    for rel in (
        "examples/basics/B06_type_first_dimensions/type_first_dimensions.sqx",
        "examples/basics/B09_multi_file_modules/main_multi_file_modules.sqx",
        "examples/applied/A02_robot_graph_planner/main_robot_graph_planner.sqx",
    ):
        compiled = compile_path(str(_REPO / rel))
        hard = [
            d
            for d in compiled.diagnostics
            if d.get("code") == "EVOLVE_BLOCK_OPAQUE_TRANSFORM"
        ]
        assert not hard, f"{rel}: {hard}"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0436 Green")
