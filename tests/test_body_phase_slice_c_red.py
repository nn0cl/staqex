"""AT-TDD Phase 1 Red: LISS-0076 Slice C — import / module-boundary phase."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_path  # noqa: E402


def _write_linked(
    tmp: Path,
    *,
    lib_package: str,
    lib_stem: str,
    lib_body: str,
    main_source: str,
) -> Path:
    (tmp / f"{lib_stem}.sqx").write_text(
        f"package {lib_package}\n\n{lib_body.strip()}\n",
        encoding="utf-8",
    )
    main = tmp / "main.sqx"
    main.write_text(main_source, encoding="utf-8")
    return main


def test_imported_execution_symbol_invisible_to_entry_theory() -> None:
    """Execution symbols from an imported module must not leak into Theory."""
    main_source = """
package com.staqex.tests.liss0076.slice_c.main

import com.staqex.tests.liss0076.slice_c.execlib

theory T {
    Operator H = n * X
}
pub fn main() -> Unit {
    State<Int> q = Coin()
    Measure q
}
"""
    with tempfile.TemporaryDirectory() as td:
        entry = _write_linked(
            Path(td),
            lib_package="com.staqex.tests.liss0076.slice_c.execlib",
            lib_stem="execlib",
            lib_body="""
execution Run {
    n = 1000
}
""",
            main_source=main_source,
        )
        result = compile_path(entry)

    codes = {diagnostic.get("code", "") for diagnostic in result.diagnostics}
    assert "PHASE_TYPE_VISIBILITY_ERROR" in codes
    assert "MODULE_NOT_FOUND_ERROR" not in codes
    assert result.ok is False


def test_imported_theory_remains_visible_to_entry_experiment() -> None:
    """Downward / same-direction cross-module Theory use stays allowed."""
    main_source = """
package com.staqex.tests.liss0076.slice_c.ok_main

import com.staqex.tests.liss0076.slice_c.theorylib

experiment E {
    theory = Ising
    observable = H
}
execution Run {
    experiment = E
    shots = 1000
}
pub fn main() -> Unit {
    State<Int> q = Coin()
    Measure q
}
"""
    with tempfile.TemporaryDirectory() as td:
        entry = _write_linked(
            Path(td),
            lib_package="com.staqex.tests.liss0076.slice_c.theorylib",
            lib_stem="theorylib",
            lib_body="""
theory Ising {
    Operator H = X + Z
}
""",
            main_source=main_source,
        )
        result = compile_path(entry)

    codes = {diagnostic.get("code", "") for diagnostic in result.diagnostics}
    assert "PHASE_TYPE_VISIBILITY_ERROR" not in codes
    assert "MODULE_NOT_FOUND_ERROR" not in codes
    assert result.ok, result.diagnostics


if __name__ == "__main__":
    test_imported_execution_symbol_invisible_to_entry_theory()
    test_imported_theory_remains_visible_to_entry_experiment()
    print("OK — body phase slice C")
