#!/usr/bin/env python3
"""Validate issue-linked active-Red tests and emit precise pytest exclusions."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import re
import sys
import tomllib
from typing import Any, Iterable


MANIFEST_PATH = Path("docs/testing/active-red-tests.toml")
WORKFLOW_DIR = Path(".github/workflows")
_GLOBAL_RED_GLOB = re.compile(r"--ignore-glob(?:=|\s+)['\"]?\*_red\.py")
_TERMINAL_STATUS_PARTS = ("done", "complete", "closed", "wont_do", "superseded")


def _diagnostic(code: str, message: str) -> str:
    return f"{code}: {message}"


def _metadata_value(text: str, field: str) -> str | None:
    expected = field.casefold()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if len(cells) >= 2 and cells[0].casefold() == expected:
                return cells[1].strip("*` ")
        match = re.match(rf"^-\s*{re.escape(field)}\s*:\s*(.+)$", stripped, re.I)
        if match:
            return match.group(1).strip().strip("*` ")
    return None


def _issue_file(root: Path, issue: str) -> Path | None:
    matches = sorted((root / "docs" / "issues").glob(f"{issue}-*.md"))
    return matches[0] if len(matches) == 1 else None


def _is_terminal_status(status: str) -> bool:
    normalized = status.casefold().replace("_", "-")
    return any(part in normalized for part in _TERMINAL_STATUS_PARTS)


def _workflow_text(root: Path) -> str:
    files = sorted((root / WORKFLOW_DIR).glob("*.yml"))
    files.extend(sorted((root / WORKFLOW_DIR).glob("*.yaml")))
    return "\n".join(path.read_text(encoding="utf-8") for path in files)


def _load_entries(root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    path = root / MANIFEST_PATH
    if not path.is_file():
        return [], [_diagnostic("ACTIVE_RED_MANIFEST_MISSING", str(MANIFEST_PATH))]
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        return [], [_diagnostic("ACTIVE_RED_MANIFEST_INVALID", str(error))]
    if document.get("version") != 1:
        return [], [_diagnostic("ACTIVE_RED_MANIFEST_VERSION", "expected version 1")]
    entries = document.get("active_red", [])
    if not isinstance(entries, list) or not all(isinstance(item, dict) for item in entries):
        return [], [_diagnostic("ACTIVE_RED_MANIFEST_INVALID", "active_red must be a table array")]
    return list(entries), []


def _required_text(entry: dict[str, Any], key: str, index: int, errors: list[str]) -> str:
    value = entry.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(
            _diagnostic("ACTIVE_RED_ENTRY_INVALID", f"entry {index} requires {key}")
        )
        return ""
    return value.strip()


def _validate_entry(
    root: Path,
    entry: dict[str, Any],
    *,
    index: int,
    as_of: date,
    seen_tests: set[str],
) -> list[str]:
    errors: list[str] = []
    issue = _required_text(entry, "issue", index, errors)
    test = _required_text(entry, "test", index, errors)
    phase = _required_text(entry, "phase", index, errors)
    _required_text(entry, "owner", index, errors)
    review_by = _required_text(entry, "review_by", index, errors)
    _required_text(entry, "review_condition", index, errors)

    if test:
        if test in seen_tests:
            errors.append(_diagnostic("ACTIVE_RED_DUPLICATE", test))
        seen_tests.add(test)
        test_path = test.split("::", 1)[0]
        if not test_path.startswith("tests/") or not (root / test_path).is_file():
            errors.append(_diagnostic("ACTIVE_RED_TEST_MISSING", test_path))

    if review_by:
        try:
            deadline = date.fromisoformat(review_by)
        except ValueError:
            errors.append(_diagnostic("ACTIVE_RED_REVIEW_DATE_INVALID", review_by))
        else:
            if deadline < as_of:
                errors.append(_diagnostic("ACTIVE_RED_REVIEW_EXPIRED", review_by))

    if issue:
        issue_path = _issue_file(root, issue)
        if issue_path is None:
            errors.append(_diagnostic("ACTIVE_RED_ISSUE_UNKNOWN", issue))
        else:
            issue_text = issue_path.read_text(encoding="utf-8")
            status = _metadata_value(issue_text, "Status")
            issue_phase = _metadata_value(issue_text, "Phase")
            if status is None or _is_terminal_status(status):
                errors.append(
                    _diagnostic("ACTIVE_RED_ISSUE_DONE", f"{issue}: {status or 'missing status'}")
                )
            if phase and issue_phase is not None and issue_phase.casefold() != phase.casefold():
                errors.append(
                    _diagnostic(
                        "ACTIVE_RED_PHASE_MISMATCH",
                        f"{issue}: manifest={phase}, issue={issue_phase}",
                    )
                )
    return errors


def validate(root: Path, *, as_of: date) -> tuple[list[dict[str, Any]], list[str]]:
    entries, errors = _load_entries(root)
    workflow = _workflow_text(root)
    if _GLOBAL_RED_GLOB.search(workflow):
        errors.append(
            _diagnostic(
                "ACTIVE_RED_GLOBAL_GLOB",
                "CI must not exclude every *_red.py file",
            )
        )
    seen_tests: set[str] = set()
    for index, entry in enumerate(entries, start=1):
        errors.extend(
            _validate_entry(
                root,
                entry,
                index=index,
                as_of=as_of,
                seen_tests=seen_tests,
            )
        )
    return entries, errors


def pytest_arguments(entries: Iterable[dict[str, Any]]) -> list[str]:
    arguments: list[str] = []
    for entry in entries:
        test = str(entry["test"])
        option = "--deselect" if "::" in test else "--ignore"
        arguments.append(f"{option}={test}")
    return arguments


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--as-of", type=date.fromisoformat, default=date.today())
    parser.add_argument("--pytest-ignore-args", action="store_true")
    args = parser.parse_args(argv)

    entries, errors = validate(args.root.resolve(), as_of=args.as_of)
    if errors:
        print("\n".join(errors))
        return 1
    if args.pytest_ignore_args:
        print("\n".join(pytest_arguments(entries)))
    else:
        print(f"ACTIVE_RED_LIFECYCLE_OK entries={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
