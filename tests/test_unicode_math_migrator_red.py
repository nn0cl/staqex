"""Acceptance tests for legacy Unicode-to-ASCII math migration."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source

_FIXTURES = _REPO / "tests" / "fixtures" / "migration"
_V01 = _FIXTURES / "v0.1"
_V1 = _FIXTURES / "v1"

_GOLDEN_NAMES = (
    "ket_basic.sqx",
    "tensor_bind.sqx",
    "adjoint_simple.sqx",
    "pipeline_preserved.sqx",
    "comments_preserved.sqx",
    "idempotent_unicode.sqx",
)


def _migrate(source: str) -> str:
    from compiler.staqex.migrate_unicode_math import migrate_unicode_math_source

    return migrate_unicode_math_source(source)


def test_migrate_unicode_math_source_matches_all_goldens() -> None:
    for name in _GOLDEN_NAMES:
        source = (_V01 / name).read_text(encoding="utf-8")
        expected = (_V1 / name).read_text(encoding="utf-8")
        assert _migrate(source) == expected, name


def test_migrated_ket_basic_still_compiles() -> None:
    source = (_V01 / "ket_basic.sqx").read_text(encoding="utf-8")
    migrated = _migrate(source)
    compiled = compile_source(migrated)
    assert compiled.ok, compiled.diagnostics


def test_migrated_adjoint_simple_still_compiles() -> None:
    source = (_V01 / "adjoint_simple.sqx").read_text(encoding="utf-8")
    migrated = _migrate(source)
    compiled = compile_source(migrated)
    assert compiled.ok, compiled.diagnostics


def test_pipeline_operator_is_preserved_beside_ket_migration() -> None:
    source = (_V01 / "pipeline_preserved.sqx").read_text(encoding="utf-8")
    migrated = _migrate(source)
    assert "|>" in migrated
    assert "|0>" in migrated
    assert "|0⟩" not in migrated


def test_comment_ascii_ket_is_not_rewritten() -> None:
    source = (_V01 / "comments_preserved.sqx").read_text(encoding="utf-8")
    migrated = _migrate(source)
    assert "// |0> in a comment must stay ASCII" in migrated
    assert "State psi = |1>" in migrated


def test_migrate_is_idempotent_on_canonical_ascii() -> None:
    source = (_V1 / "idempotent_unicode.sqx").read_text(encoding="utf-8")
    assert _migrate(source) == source


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0069 Slice B Phase 2 Green")
