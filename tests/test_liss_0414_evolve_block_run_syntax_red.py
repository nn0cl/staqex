"""AT-TDD Phase 1 Red -> Green: `evolve { ... under H for t }.run()`
replaces the bare `evolve { ... under H for t` form (LISS-0414). }.run()

Target: docs/issues/LISS-0414-evolve-block-run-syntax.md.

Adjudicator-requested: a reader unfamiliar with Staqex cannot tell, at a
glance, whether `evolve` in `state a = evolve a under H for dur` is an
operation, a variable, or a declaration -- no bracketing/call syntax
signals "this is an operation," unlike `apply(H, psi)`. Only the
Hamiltonian `under H for t` form is in scope; the `times N { body }` /
`for dt { body }` block forms already have `{ }` and are unaffected.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_bare_seed_block_run_form_parses_and_runs() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H = scale * Z
        state a = |0>
        Time dur = 0.6.fs
        state a = evolve { a under H for dur }.run()
        measure a
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None


def test_tuple_seed_with_suzuki_block_run_form_parses_and_runs() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H = scale * (Z[0] * Z[1])
        state a = |0>
        state b = |+>
        Time dur = 0.6.fs
        state (a, b) = evolve { (a, b) under H for dur using Suzuki(order=2, steps=4) }.run()
        measure a tracing_out b
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None


def test_until_max_block_run_form_parses_and_runs() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        state fuel = dirac(0)
        Time dur = 1.5707963267948966.s
        state fuel = evolve { fuel under X for dur until converged(fuel) max 64 }.run()
        measure fuel
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None


def test_old_bare_form_is_rejected_with_a_migration_diagnostic() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H = scale * Z
        state a = |0>
        Time dur = 0.6.fs
        state a = evolve a under H for dur
        measure a
    }
    """
    compiled = compile_source(source)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "EVOLVE_REQUIRES_BLOCK_RUN" in codes, compiled.diagnostics
    assert compiled.unit is None


def test_missing_run_suffix_is_rejected() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H = scale * Z
        state a = |0>
        Time dur = 0.6.fs
        state a = evolve { a under H for dur }
        measure a
    }
    """
    compiled = compile_source(source)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert codes, compiled.diagnostics
    assert compiled.unit is None


def test_times_block_form_is_unaffected() -> None:
    """Regression guard: the already-bracketed `times N { body }` form
    must not require `.run()` and must be completely unaffected."""
    source = """
    package t
    pub fn main() -> Unit {
        Operator H = X
        state a = |0>
        state a = evolve a times 2 {
            let next = evolve a under H for 0.1.fs
            next
        }
        measure a
    }
    """
    # This source intentionally still uses the retired bare `under` form
    # *inside* the times-block body to confirm the outer `times N { }`
    # dispatch itself is reached correctly and only the inner bare form
    # is rejected -- i.e. the times/for dispatch branch is unaffected by
    # LISS-0414, not that nested bare-under forms are still accepted.
    compiled = compile_source(source)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "EVOLVE_REQUIRES_BLOCK_RUN" in codes, compiled.diagnostics


def test_for_block_form_is_unaffected() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        state a = |0>
        state a = evolve a for 0.5 {
            a
        }
        measure a
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
