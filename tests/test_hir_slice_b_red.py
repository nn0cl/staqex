"""AT-TDD Phase 1 Red: LISS-0080 Slice B — declaration phase on HIR decls."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _load_hir_api():
    from compiler.staqex.hir import HirDecl, HirModule, build_hir

    return HirDecl, HirModule, build_hir


def test_hir_decl_and_declarations_exist() -> None:
    """Slice B exposes HirDecl with phase and HirModule.declarations."""
    HirDecl, HirModule, build_hir = _load_hir_api()
    assert HirDecl is not None
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    hir = build_hir(compiled.checker)
    assert hasattr(hir, "declarations"), "HirModule must expose declaration phases"
    assert hir.declarations, "unscoped Kernel main must appear in declarations"


def test_scientific_scope_phases_recorded_on_hir() -> None:
    """Theory/experiment scope kinds map to HIR declaration phases."""
    _, HirModule, build_hir = _load_hir_api()
    compiled = compile_source(
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
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    assert compiled.scope_contracts is not None

    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
    )
    assert isinstance(hir, HirModule)
    decls = dict(hir.declarations)
    assert decls["Ising"].phase == "theory"
    assert decls["GroundState"].phase == "experiment"
    assert decls["main"].phase == "kernel"


def test_build_hir_without_scope_contracts_defaults_kernel_phase() -> None:
    """Slice A call shape remains valid; unscoped decls default to kernel."""
    _, _, build_hir = _load_hir_api()
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State q = Coin()
            Measure q
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    hir = build_hir(compiled.checker)
    decls = dict(hir.declarations)
    assert decls["main"].phase == "kernel"


def test_declaration_mapping_is_immutable() -> None:
    _, _, build_hir = _load_hir_api()
    compiled = compile_source(
        """
        package t
        theory T { Operator H = X }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )
    hir = build_hir(compiled.checker, scope_contracts=compiled.scope_contracts)
    try:
        hir.declarations["T"] = hir.declarations["T"]  # type: ignore[index]
        mutated = True
    except TypeError:
        mutated = False
    assert mutated is False, "HIR declarations mapping must be immutable"


def main() -> None:
    test_hir_decl_and_declarations_exist()
    print("PASS test_hir_decl_and_declarations_exist")
    test_scientific_scope_phases_recorded_on_hir()
    print("PASS test_scientific_scope_phases_recorded_on_hir")
    test_build_hir_without_scope_contracts_defaults_kernel_phase()
    print("PASS test_build_hir_without_scope_contracts_defaults_kernel_phase")
    test_declaration_mapping_is_immutable()
    print("PASS test_declaration_mapping_is_immutable")
    print("OK - LISS-0080 Slice B Phase 1 Red")


if __name__ == "__main__":
    main()
