"""AT-TDD Phase 1 Red: reject legacy untyped functions (LISS-0021)."""

from __future__ import annotations

import sys
from pathlib import Path
import re

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def test_untyped_library_function_is_rejected() -> None:
    codes = _codes(
        """
        fn build_link_witness() {
            Float ideal_correlation = 1.0
        }
        """
    )

    assert "MISSING_RETURN_TYPE" in codes


def test_untyped_method_is_rejected() -> None:
    codes = _codes(
        """
        class Box {
            val value: Int

            fn next() {
                State<Int> result = Dirac(this.value + 1)
            }
        }
        """
    )

    assert "MISSING_RETURN_TYPE" in codes


def test_bare_main_is_rejected() -> None:
    codes = _codes(
        """
        pub fn main() {
            State<Int> answer = Dirac(1)
            Measure answer
        }
        """
    )

    assert "MISSING_RETURN_TYPE" in codes


def test_init_is_the_only_untyped_function_exception() -> None:
    codes = _codes(
        """
        class Box {
            val value: Int

            fn init(value: Int) {
                this.value = value
            }
        }
        """
    )

    assert "MISSING_RETURN_TYPE" not in codes


def test_official_examples_have_no_legacy_untyped_declarations() -> None:
    offenders: list[str] = []
    declaration = re.compile(r"^(?:(?:public|pub)\s+)?fn\s+\w+\s*\(")
    for path in sorted(Path("examples").rglob("*.sqx")):
        source = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(source.splitlines(), start=1):
            stripped = line.strip()
            if "fn init(" in stripped:
                continue
            if declaration.match(stripped) and "->" not in stripped:
                offenders.append(f"{path}:{line_no}: {stripped}")

    assert not offenders, "legacy untyped declarations:\n" + "\n".join(offenders)


if __name__ == "__main__":
    tests = [
        test_untyped_library_function_is_rejected,
        test_untyped_method_is_rejected,
        test_bare_main_is_rejected,
        test_init_is_the_only_untyped_function_exception,
        test_official_examples_have_no_legacy_untyped_declarations,
    ]
    for test in tests:
        test()
    print("OK — missing return annotation tests")
