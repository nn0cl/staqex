"""AT-TDD Phase 1 Red: LISS-0080 Slice C — effects on HIR decls."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _hir(source: str, *, scope_contracts=None):
    from compiler.staqex.hir import build_hir

    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    sc = scope_contracts if scope_contracts is not None else compiled.scope_contracts
    return build_hir(compiled.checker, scope_contracts=sc)


def test_hir_decl_has_effects_field() -> None:
    """HirDecl must expose an effects field after Slice C."""
    from compiler.staqex.hir import HirDecl

    hir = _hir(
        """
        package t
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    decl = hir.declarations["main"]
    assert hasattr(decl, "effects"), "HirDecl must have an effects field"
    assert isinstance(decl.effects, frozenset)


def test_declared_function_effects_recorded_on_hir() -> None:
    """Explicit effects {Inspect} on a fn appear in HirDecl.effects."""
    hir = _hir(
        """
        package t
        fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
            return Inspect(x)
        }
        pub fn main() -> Unit {
            State psi = Dirac(0.0)
            State viewed = inspect_state(psi)
            Measure viewed
        }
        """
    )
    decls = dict(hir.declarations)
    assert decls["inspect_state"].effects == frozenset({"Inspect"})


def test_main_entry_effects_is_empty() -> None:
    """main has no explicit effects declaration; HIR records frozenset().

    Full-effects permission for main is an implicit typecheck rule — not a
    declared contract. Slice C records only explicit declarations; mapping
    main's implicit permission to a phase is deferred to a future ADR
    (execution-phase unification).
    """
    hir = _hir(
        """
        package t
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert hir.declarations["main"].effects == frozenset()


def test_scope_decl_effects_is_empty() -> None:
    """Scientific-scope decls (theory, experiment) carry no effects."""
    hir = _hir(
        """
        package t
        theory Ising { Operator H = X + Z }
        experiment GroundState { theory = Ising }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert hir.declarations["Ising"].effects == frozenset()
    assert hir.declarations["GroundState"].effects == frozenset()


def test_effects_mapping_is_immutable() -> None:
    """HirDecl.effects is a frozenset (immutable)."""
    hir = _hir(
        """
        package t
        fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
            return Inspect(x)
        }
        pub fn main() -> Unit {
            State psi = Dirac(0.0)
            State viewed = inspect_state(psi)
            Measure viewed
        }
        """
    )
    effects = hir.declarations["inspect_state"].effects
    try:
        effects.add("Measure")  # type: ignore[attr-defined]
        mutated = True
    except AttributeError:
        mutated = False
    assert mutated is False, "HirDecl.effects must be a frozenset (immutable)"


def main() -> None:
    test_hir_decl_has_effects_field()
    print("PASS test_hir_decl_has_effects_field")
    test_declared_function_effects_recorded_on_hir()
    print("PASS test_declared_function_effects_recorded_on_hir")
    test_main_entry_effects_is_empty()
    print("PASS test_main_entry_effects_is_empty")
    test_scope_decl_effects_is_empty()
    print("PASS test_scope_decl_effects_is_empty")
    test_effects_mapping_is_immutable()
    print("PASS test_effects_mapping_is_immutable")
    print("OK - LISS-0080 Slice C Phase 1 Red")


if __name__ == "__main__":
    main()
