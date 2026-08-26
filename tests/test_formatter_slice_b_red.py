"""AT-TDD Phase 1 Red: LISS-0072 Slice B — formatter + round-trip + CLI."""

from __future__ import annotations

import io
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import fields, is_dataclass
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import main
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
)


def _format(source: str) -> str:
    from compiler.staqex.format import format_source

    return format_source(source)


def _run_format(argv: list[str]) -> tuple[int, str, str]:
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(["format", *argv])
        except SystemExit as exc:
            raw = exc.code
            if raw is None:
                code = 0
            elif isinstance(raw, int):
                code = raw
            else:
                code = 1
    return int(code), out.getvalue(), err.getvalue()


def _strip_spans(value):
    if is_dataclass(value):
        data = {}
        for field in fields(value):
            if field.name == "span":
                continue
            data[field.name] = _strip_spans(getattr(value, field.name))
        return (type(value).__name__, data)
    if isinstance(value, list):
        return [_strip_spans(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_strip_spans(item) for item in value)
    if isinstance(value, dict):
        return {key: _strip_spans(item) for key, item in value.items()}
    return value


def test_format_source_matches_migration_goldens() -> None:
    for name in _GOLDEN_NAMES:
        source = (_V01 / name).read_text(encoding="utf-8")
        expected = (_V1 / name).read_text(encoding="utf-8")
        assert _format(source) == expected, name


def test_format_round_trip_preserves_structural_ast() -> None:
    # ASCII source remains lossless and reparses to the same AST.
    for name in ("ket_basic.sqx",):
        source = (_V01 / name).read_text(encoding="utf-8")
        formatted = _format(source)
        original = compile_source(source)
        reparsed = compile_source(formatted)
        assert original.ok, original.diagnostics
        assert reparsed.ok, reparsed.diagnostics
        assert _strip_spans(reparsed.unit) == _strip_spans(original.unit), name


def test_format_adjoint_dagger_rewrite_still_compiles() -> None:
    source = (_V01 / "adjoint_simple.sqx").read_text(encoding="utf-8")
    formatted = _format(source)
    assert formatted == source
    original = compile_source(source)
    reparsed = compile_source(formatted)
    assert original.ok, original.diagnostics
    assert reparsed.ok, reparsed.diagnostics


def test_format_preserves_comment_text() -> None:
    source = (_V01 / "comments_preserved.sqx").read_text(encoding="utf-8")
    formatted = _format(source)

    assert "// |0> in a comment must stay ASCII" in formatted


def test_format_preview_prints_canonical_source_without_rewriting() -> None:
    path = _V01 / "ket_basic.sqx"
    before = path.read_text(encoding="utf-8")
    expected = (_V1 / "ket_basic.sqx").read_text(encoding="utf-8")

    code, stdout, _stderr = _run_format([str(path)])

    assert code == 0
    assert stdout == expected
    assert path.read_text(encoding="utf-8") == before


def test_format_write_rewrites_temp_file_in_place() -> None:
    src = (_V01 / "ket_basic.sqx").read_text(encoding="utf-8")
    expected = (_V1 / "ket_basic.sqx").read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / "ket_basic.sqx"
        target.write_text(src, encoding="utf-8")

        code, stdout, _stderr = _run_format([str(target), "--write"])

        assert code == 0
        assert stdout == ""
        assert target.read_text(encoding="utf-8") == expected


def test_format_check_accepts_canonical_ascii_source() -> None:
    path = _V01 / "ket_basic.sqx"

    code, stdout, _stderr = _run_format([str(path), "--check"])

    assert code == 0
    assert stdout == ""


def test_format_output_writes_separate_path() -> None:
    path = _V01 / "ket_basic.sqx"
    expected = (_V1 / "ket_basic.sqx").read_text(encoding="utf-8")
    before = path.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        out_path = Path(td) / "out.sqx"
        code, stdout, _stderr = _run_format([str(path), "-o", str(out_path)])
        assert code == 0
        assert stdout == ""
        assert out_path.read_text(encoding="utf-8") == expected

    assert path.read_text(encoding="utf-8") == before


if __name__ == "__main__":
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001 — Red harness
                failures += 1
                print(f"FAIL {name}: {type(exc).__name__}: {exc}")
    if failures:
        raise SystemExit(f"Red confirmed: {failures} failure(s)")
    print("OK - LISS-0072 Slice B Phase 1 Red")
