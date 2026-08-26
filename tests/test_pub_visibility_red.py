"""AT-TDD Phase 1 Red: make ``pub`` the only public visibility spelling."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_pub_function_is_accepted() -> None:
    codes = _codes(
        """
        pub fn advance() -> State<Int> {
            Dirac(1)
        }
        """
    )

    assert "RETIRED_KEYWORD" not in codes
    assert "PARSE_ERROR" not in codes


def test_public_is_rejected_without_compatibility_fallback() -> None:
    codes = _codes(
        """
        public fn advance() -> State<Int> {
            Dirac(1)
        }
        """
    )

    assert "RETIRED_KEYWORD" in codes


def test_official_examples_have_no_active_public_modifier() -> None:
    offenders: list[str] = []
    declaration = re.compile(r"^\s*public\s+(?:fn|class|struct|enum|interface)\b")
    for path in sorted(Path("examples").rglob("*.sqx")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if declaration.match(line):
                offenders.append(f"{path}:{line_no}: {line.strip()}")

    assert not offenders, "active public declarations:\n" + "\n".join(offenders)


if __name__ == "__main__":
    test_pub_function_is_accepted()
    test_public_is_rejected_without_compatibility_fallback()
    test_official_examples_have_no_active_public_modifier()
    print("OK — pub visibility Red tests")
