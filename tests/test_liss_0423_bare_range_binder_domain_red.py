"""AT-TDD Phase 1 Red -> Green: bare-range binder domains (`i In 0..n-1`),
retiring `Index<...>` as a binder-domain spelling.

Target: docs/issues/LISS-0423-bare-range-binder-domains.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_bare_range_binder_domain_works() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Sigma (i In 0..1) { Z[i] }
        Operator H = scale * H_raw
        State (a, b) = (|0>, |0>)
        State (a, b) = Evolve { (a, b) under H for 0.1.fs }.run()
        Measure a tracing_out b
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None


def test_bare_range_multi_binding_with_guard_works() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Sigma (i In 0..2, j In 0..2) where i < j {
            Z[i] * Z[j]
        }
        Operator H = scale * H_raw
        State (a, b, c) = (|0>, |0>, |0>)
        State (a, b, c) = Evolve { (a, b, c) under H for 0.1.fs using Suzuki(order = 2, steps = 2) }.run()
        Measure a tracing_out b, c
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit)
    assert result.measure is not None


def test_bare_range_with_variable_endpoint_works() -> None:
    """`0..n-1` with a runtime-scoped `n` -- the exact shape LISS-0423 was
    motivated by (S02's objective_hamiltonian previously hardcoded
    `Index<0..7>`, disconnected from `Int n = 8`)."""
    src = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = Sigma (i In 0..register-1) { Z[i] }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics


def test_index_range_form_is_retired() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Operator H = Sigma (i In Index<0..2>) { Z[i] }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert not compiled.ok
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "BINDER_DOMAIN_INDEX_RETIRED" in codes, compiled.diagnostics


def test_index_single_arg_form_is_retired() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Operator H = Sigma (i In Index<4>) { Z[i] }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert not compiled.ok
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "BINDER_DOMAIN_INDEX_RETIRED" in codes, compiled.diagnostics


def test_rev_index_form_is_retired() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Operator H = Sigma (i In rev(Index<0..2>)) { Z[i] }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert not compiled.ok
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "BINDER_DOMAIN_INDEX_RETIRED" in codes, compiled.diagnostics


def test_rev_bare_range_still_works() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = Sigma (i In rev(0..2)) { Z[i] }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0423 Slice B Phase 2 Green")
