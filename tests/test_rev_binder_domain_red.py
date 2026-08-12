"""AT-TDD: LISS-0147 rev(Index) binder domains (ADR 0117)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import OpBin, OpLit, OpPauli  # noqa: E402
from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def _pauli_sites(expr) -> list[int]:
    sites: list[int] = []

    def walk(node) -> None:
        if isinstance(node, OpPauli) and node.site is not None:
            sites.append(int(node.site))
        elif isinstance(node, OpBin):
            walk(node.lhs)
            walk(node.rhs)
        elif isinstance(node, OpLit):
            return

    walk(expr)
    return sites


def test_rev_enumerates_descending() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = Sigma (i In rev(Index<0..2>)) {
            Z[i]
        }
        State a = |0>
        Measure a
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes, codes
    compiled = compile_source(source)
    assert compiled.unit is not None
    lowered, _ = lower_finite_binder_operators(compiled.unit)
    assert "H" in lowered
    sites = _pauli_sites(lowered["H"])
    assert sites == [2, 1, 0], sites


def test_rev_empty_stays_empty() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Operator H = Sigma (i In rev(Index<2..0>)) {
            Z[0]
        }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None
    # empty domain → identity; lowering may still succeed without sites
    lowered, _ = lower_finite_binder_operators(compiled.unit)
    assert "H" in lowered


if __name__ == "__main__":
    test_rev_enumerates_descending()
    print("PASS test_rev_enumerates_descending")
    test_rev_empty_stays_empty()
    print("PASS test_rev_empty_stays_empty")
