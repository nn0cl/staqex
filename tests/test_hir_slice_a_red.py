"""AT-TDD Phase 1 Red: LISS-0080 Slice A — immutable HIR DTO + build API."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _load_hir_api():
    """Slice A Green must export these from compiler.staqex.hir."""
    from compiler.staqex.hir import HirModule, build_hir

    return HirModule, build_hir


def test_hir_module_importable() -> None:
    """Missing hir module is the expected Red compile/import failure."""
    HirModule, build_hir = _load_hir_api()
    assert HirModule is not None
    assert callable(build_hir)


def test_build_hir_from_typechecker_exposes_symbols_and_typed_map() -> None:
    """Immutable HIR carries symbol table + typed expression map from TypeChecker."""
    HirModule, build_hir = _load_hir_api()
    source = """
    package t
    pub fn main() -> Unit {
        State s = |0>
        Measure s
    }
    """
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None

    hir = build_hir(compiled.checker)
    assert isinstance(hir, HirModule)
    assert hir.symbols, "HIR must expose resolved symbols from TypeChecker.env"
    assert "s" in hir.symbols
    assert hir.symbols["s"].kind == "State"
    assert hir.typed, "HIR must expose typed expression map from TypeChecker.typed"
    # Mapping is frozen / immutable for downstream consumers.
    assert type(hir.symbols).__name__ in {"MappingProxyType", "dict"} or hasattr(
        hir.symbols, "get"
    )
    try:
        hir.symbols["s"] = hir.symbols["s"]  # type: ignore[index]
        mutated = True
    except TypeError:
        mutated = False
    assert mutated is False, "HIR symbols mapping must be immutable"


def test_build_hir_does_not_require_evaluator_rewire() -> None:
    """Slice A is API/DTO only — compile_source remains authoritative."""
    _, build_hir = _load_hir_api()
    source = """
    package t
    pub fn main() -> Unit {
        State q = Coin()
        Measure q
    }
    """
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    hir = build_hir(compiled.checker)
    assert hir is not None
    # Evaluator path is unchanged: no HirModule field required on CompileResult yet.
    assert not hasattr(compiled, "hir") or getattr(compiled, "hir", None) is None


def main() -> None:
    test_hir_module_importable()
    print("PASS test_hir_module_importable")
    test_build_hir_from_typechecker_exposes_symbols_and_typed_map()
    print("PASS test_build_hir_from_typechecker_exposes_symbols_and_typed_map")
    test_build_hir_does_not_require_evaluator_rewire()
    print("PASS test_build_hir_does_not_require_evaluator_rewire")
    print("OK - LISS-0080 Slice A Phase 1 Red")


if __name__ == "__main__":
    main()
