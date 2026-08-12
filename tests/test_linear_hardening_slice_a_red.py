"""AT-TDD Phase 1 Red: LISS-0114 Slice A — pipeline hard-fail + Gherkin."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def test_implicit_discard_fails_compile_source() -> None:
    """LINEAR_IMPLICIT_DISCARD must hard-fail CompileResult.ok via pipeline."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> leftover = Coin()
            State<Int> q = Coin()
            Measure q
        }
        """
    )
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(compiled.diagnostics), (
        f"expected LINEAR_IMPLICIT_DISCARD in compile diagnostics, "
        f"got {_codes(compiled.diagnostics)}"
    )
    assert compiled.ok is False, "linear discard must set CompileResult.ok=False"


def test_duplicate_alias_fails_compile_source() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            State<Int> alias = q
            Measure alias
        }
        """
    )
    assert "LINEAR_DUPLICATE_USE" in _codes(compiled.diagnostics)
    assert compiled.ok is False


def main() -> None:
    test_implicit_discard_fails_compile_source()
    print("PASS test_implicit_discard_fails_compile_source")
    test_duplicate_alias_fails_compile_source()
    print("PASS test_duplicate_alias_fails_compile_source")
    print("OK - LISS-0114 Slice A Phase 1 Red")


if __name__ == "__main__":
    main()
