#!/usr/bin/env python3
"""Validate explicit Canonical Document Register entries."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VALID_LAYERS = {"Entry", "Canonical", "Evidence", "Archive"}
VALID_STATUSES = {"Current", "Historical"}
REGISTER_NAMES = {"canonical-document-register.md"}
PLACEHOLDER = re.compile(r"<[^>]+>")


def cells(line: str) -> list[str]:
    return [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]


def is_placeholder(value: str) -> bool:
    return not value or bool(PLACEHOLDER.search(value))


def paths_from(value: str) -> list[str]:
    return [item.strip().strip("`") for item in value.split(";") if item.strip()]


def fail(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path}: {message}")


def check_register(path: Path, root: Path, errors: list[str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if "canonical_key" in line and "canonical_path" in line),
        None,
    )
    if header_index is None:
        fail(errors, path, "missing register table header")
        return

    header = cells(lines[header_index])
    required = {"canonical_key", "layer", "status", "entry_path", "canonical_path", "source_paths"}
    missing = required - set(header)
    if missing:
        fail(errors, path, f"missing columns: {', '.join(sorted(missing))}")
        return

    indexes = {name: header.index(name) for name in required}
    keys: set[str] = set()
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            continue
        row = cells(line)
        if len(row) < len(header) or is_placeholder(row[indexes["canonical_key"]]):
            continue
        key = row[indexes["canonical_key"]]
        layer = row[indexes["layer"]]
        status = row[indexes["status"]]
        entry = row[indexes["entry_path"]]
        canonical = row[indexes["canonical_path"]]
        sources = paths_from(row[indexes["source_paths"]])

        if key in keys:
            fail(errors, path, f"duplicate canonical_key: {key}")
        keys.add(key)
        if layer not in VALID_LAYERS:
            fail(errors, path, f"invalid layer for {key}: {layer}")
        if status not in VALID_STATUSES:
            fail(errors, path, f"invalid status for {key}: {status}")

        declared_paths = [("entry_path", entry), ("canonical_path", canonical)]
        for field, value in declared_paths:
            if is_placeholder(value):
                fail(errors, path, f"{key} has a placeholder {field}")
                continue
            candidate = root / value
            if not candidate.is_file():
                fail(errors, path, f"{key} {field} does not exist: {value}")
            if "/archive/" in f"/{value.lower().strip('/')}/":
                fail(errors, path, f"{key} {field} points into an Archive path: {value}")

        if status == "Current" and not sources:
            fail(errors, path, f"Current entry has no source_paths: {key}")
        for source in sources:
            if is_placeholder(source):
                continue
            if not (root / source).is_file():
                fail(errors, path, f"{key} source path does not exist: {source}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    registers = [path for path in root.rglob("*.md") if path.name in REGISTER_NAMES]
    errors: list[str] = []
    for register in registers:
        check_register(register, root, errors)
    if errors:
        print("Document lifecycle check failed:", file=sys.stderr)
        print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Document lifecycle check passed ({len(registers)} register(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
