"""Acceptance tests for the legacy Unicode-to-ASCII migrate CLI."""

from __future__ import annotations

import io
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import main

_FIXTURES = _REPO / "tests" / "fixtures" / "migration"
_V01 = _FIXTURES / "v0.1"
_V1 = _FIXTURES / "v1"
_KET = "ket_basic.sqx"


def _run_migrate(argv: list[str]) -> tuple[int, str, str]:
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(["migrate", *argv])
        except SystemExit as exc:
            raw = exc.code
            if raw is None:
                code = 0
            elif isinstance(raw, int):
                code = raw
            else:
                code = 1
    return int(code), out.getvalue(), err.getvalue()


def test_migrate_preview_prints_golden_and_leaves_file() -> None:
    path = _V01 / _KET
    before = path.read_text(encoding="utf-8")
    expected = (_V1 / _KET).read_text(encoding="utf-8")
    code, stdout, _stderr = _run_migrate([str(path)])
    assert code == 0
    assert stdout == expected
    assert path.read_text(encoding="utf-8") == before


def test_migrate_write_rewrites_temp_file_in_place() -> None:
    src = (_V01 / _KET).read_text(encoding="utf-8")
    expected = (_V1 / _KET).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        target = Path(td) / _KET
        target.write_text(src, encoding="utf-8")
        code, stdout, _stderr = _run_migrate([str(target), "--write"])
        assert code == 0
        assert stdout == ""
        assert target.read_text(encoding="utf-8") == expected


def test_migrate_check_exits_one_on_legacy_unicode_drift() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / _KET
        path.write_text("State psi = |0⟩\n", encoding="utf-8")
        code, stdout, _stderr = _run_migrate([str(path), "--check"])
    assert code == 1
    assert stdout == ""


def test_migrate_check_exits_zero_when_already_canonical() -> None:
    path = _V1 / _KET
    code, stdout, _stderr = _run_migrate([str(path), "--check"])
    assert code == 0
    assert stdout == ""


def test_migrate_output_writes_separate_path() -> None:
    path = _V01 / _KET
    expected = (_V1 / _KET).read_text(encoding="utf-8")
    before = path.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        out_path = Path(td) / "out.sqx"
        code, stdout, _stderr = _run_migrate([str(path), "-o", str(out_path)])
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
    print("OK - LISS-0069 Slice C Phase 3 Refactor")
