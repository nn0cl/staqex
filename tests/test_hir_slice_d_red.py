"""AT-TDD Phase 1 Red: LISS-0080 Slice D — provenance + HIR verifier."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _hir(source: str):
    from compiler.staqex.hir import build_hir

    c = compile_source(source)
    assert c.ok, c.diagnostics
    return build_hir(c.checker, scope_contracts=c.scope_contracts, unit=c.unit), c


# ---------------------------------------------------------------------------
# Provenance: decl-level source span
# ---------------------------------------------------------------------------

def test_hir_decl_has_span() -> None:
    """HirDecl must carry a source span after Slice D."""
    hir, _ = _hir(
        """
        package t
        pub fn main() -> Unit {
            State<Int> observed = coin()
            measure observed
        }
        """
    )
    decl = hir.declarations["main"]
    assert hasattr(decl, "span"), "HirDecl must have a span field"
    span = decl.span
    assert hasattr(span, "line") and hasattr(span, "col")
    assert span.line > 0


def test_scope_decl_span_recorded() -> None:
    """Scientific-scope decl spans are preserved in HIR."""
    hir, _ = _hir(
        """
        package t
        theory Ising { Operator H = X + Z }
        pub fn main() -> Unit {
            State<Int> observed = coin()
            measure observed
        }
        """
    )
    ising = hir.declarations["Ising"]
    assert hasattr(ising, "span")
    assert ising.span.line > 0


def test_function_decl_span_recorded() -> None:
    """Named function decl spans are preserved in HIR."""
    hir, _ = _hir(
        """
        package t
        fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
            return inspect(x)
        }
        pub fn main() -> Unit {
            State psi = dirac(0.0)
            State viewed = inspect_state(psi)
            measure viewed
        }
        """
    )
    decl = hir.declarations["inspect_state"]
    assert hasattr(decl, "span")
    assert decl.span.line > 0


# ---------------------------------------------------------------------------
# HIR verifier
# ---------------------------------------------------------------------------

def test_verify_hir_importable() -> None:
    """verify_hir must be importable from compiler.staqex.hir after Slice D."""
    from compiler.staqex.hir import verify_hir  # noqa: F401

    assert callable(verify_hir)


def test_verify_hir_accepts_valid_module() -> None:
    """verify_hir returns no diagnostics for a well-formed HIR."""
    from compiler.staqex.hir import verify_hir

    hir, _ = _hir(
        """
        package t
        theory Ising { Operator H = X + Z }
        fn inspect_state(x: State<Float>) -> State<Float> effects { Inspect } {
            return inspect(x)
        }
        pub fn main() -> Unit {
            State<Int> observed = coin()
            measure observed
        }
        """
    )
    diags = verify_hir(hir)
    assert diags == [], f"expected no diagnostics, got {diags}"


def test_verify_hir_rejects_unknown_phase() -> None:
    """verify_hir reports a diagnostic for an unrecognised phase value."""
    from compiler.staqex.hir import HirDecl, HirModule, verify_hir
    from types import MappingProxyType

    bad_decl = HirDecl(name="x", phase="unknown_phase", effects=frozenset())
    module = HirModule(
        symbols=MappingProxyType({}),
        typed=MappingProxyType({}),
        declarations=MappingProxyType({"x": bad_decl}),
    )
    diags = verify_hir(module)
    assert any("phase" in str(d).lower() or "phase" in d.get("message", "").lower() for d in diags), (
        f"expected a phase diagnostic, got {diags}"
    )


def test_verify_hir_rejects_unknown_effect() -> None:
    """verify_hir reports a diagnostic for an unrecognised effect value."""
    from compiler.staqex.hir import HirDecl, HirModule, verify_hir
    from types import MappingProxyType

    bad_decl = HirDecl(name="f", phase="kernel", effects=frozenset({"UnknownEffect"}))
    module = HirModule(
        symbols=MappingProxyType({}),
        typed=MappingProxyType({}),
        declarations=MappingProxyType({"f": bad_decl}),
    )
    diags = verify_hir(module)
    assert any("effect" in str(d).lower() or "effect" in d.get("message", "").lower() for d in diags), (
        f"expected an effect diagnostic, got {diags}"
    )


def main() -> None:
    test_hir_decl_has_span()
    print("PASS test_hir_decl_has_span")
    test_scope_decl_span_recorded()
    print("PASS test_scope_decl_span_recorded")
    test_function_decl_span_recorded()
    print("PASS test_function_decl_span_recorded")
    test_verify_hir_importable()
    print("PASS test_verify_hir_importable")
    test_verify_hir_accepts_valid_module()
    print("PASS test_verify_hir_accepts_valid_module")
    test_verify_hir_rejects_unknown_phase()
    print("PASS test_verify_hir_rejects_unknown_phase")
    test_verify_hir_rejects_unknown_effect()
    print("PASS test_verify_hir_rejects_unknown_effect")
    print("OK - LISS-0080 Slice D Phase 1 Red")


if __name__ == "__main__":
    main()
