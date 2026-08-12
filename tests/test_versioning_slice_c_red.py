"""AT-TDD Phase 1 Red: LISS-0072 Slice C — versioning and fix-it surfacing."""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import main
from compiler.staqex.pipeline import compile_source


def _run_check_source(source: str) -> tuple[int, str, str]:
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(["check", "-e", source])
        except SystemExit as exc:
            raw = exc.code
            if raw is None:
                code = 0
            elif isinstance(raw, int):
                code = raw
            else:
                code = 1
    return int(code), out.getvalue(), err.getvalue()


def test_staqex_version_1_0_metadata_compiles() -> None:
    compiled = compile_source(
        """
        package demo
        staqex_version = "1.0"

        pub fn main() -> Unit {
            State psi = |0>
            Measure psi
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_unsupported_staqex_version_fails_with_named_diagnostic() -> None:
    compiled = compile_source(
        """
        package demo
        staqex_version = "9.9"

        pub fn main() -> Unit {
            State psi = |0>
            Measure psi
        }
        """
    )

    assert any(
        diagnostic.get("code") == "UNSUPPORTED_QPEX_VERSION"
        for diagnostic in compiled.diagnostics
    ), compiled.diagnostics


def test_check_surfaces_retired_keyword_fix_it() -> None:
    code, _stdout, stderr = _run_check_source(
        """
        package demo
        public fn main() -> Unit {
            State psi = |0>
            observe psi
        }
        """
    )

    assert code == 1
    assert "RETIRED_KEYWORD" in stderr
    assert "fix-it: use `pub`" in stderr or "fix-it: use `Measure`" in stderr


def test_check_does_not_invent_fix_it_for_forbidden_keyword() -> None:
    code, _stdout, stderr = _run_check_source(
        """
        package demo
        pub fn main() -> Unit {
            if true {
                Measure |0>
            }
        }
        """
    )

    assert code == 1
    assert "FORBIDDEN_KEYWORD" in stderr
    assert "fix-it:" not in stderr


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
    print("OK - LISS-0072 Slice C Phase 1 Red")
