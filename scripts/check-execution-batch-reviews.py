#!/usr/bin/env python3
"""Validate bounded execution-batch review records.

This is intentionally a standard-library-only check. It validates the
repository record and Issue references; it does not infer design quality or
authenticate a human reviewer.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


RECORD_GLOB = "execution-batch-*.json"
ALLOWED_STATUSES = {
    "approved_for_execution",
    "in_progress",
    "awaiting_post_review",
    "post_reviewed",
    "rejected",
    "expired",
}
ISSUE_PATTERN = re.compile(r"^LISS-[0-9]{4}$")
COMMIT_PATTERN = re.compile(r"^[0-9a-fA-F]{40}$")
REQUIRED_FIELDS = {
    "schema_version",
    "batch_id",
    "status",
    "approval_type",
    "approved_by",
    "approved_at",
    "expires_at",
    "execution_branch",
    "approval_commit",
    "issue_ids",
    "approved_scope",
    "allowed_paths",
    "allowed_phases",
    "allowed_operations",
    "invalidating_triggers",
    "post_review_required",
}


def fail(path: Path, message: str) -> None:
    raise ValueError(f"{path}: {message}")


def parse_timestamp(path: Path, field: str, value: object) -> datetime:
    if not isinstance(value, str):
        fail(path, f"{field} must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        fail(path, f"{field} is not valid ISO-8601: {error}")
    if parsed.tzinfo is None:
        fail(path, f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def require_string(path: Path, data: dict[str, object], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        fail(path, f"{field} must be a non-empty string")
    return value


def require_string_list(path: Path, data: dict[str, object], field: str) -> list[str]:
    value = data.get(field)
    if not isinstance(value, list) or not value:
        fail(path, f"{field} must be a non-empty array")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        fail(path, f"{field} must contain only non-empty strings")
    return value


def changed_files_since(repository_root: Path, approval_commit: str) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{approval_commit}..HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError(f"could not inspect changes since {approval_commit}: {error}")
    return [line for line in result.stdout.splitlines() if line]


def is_allowed_path(path: str, allowed_paths: list[str]) -> bool:
    from fnmatch import fnmatchcase

    return any(fnmatchcase(path, pattern) for pattern in allowed_paths)


def validate_record(
    path: Path,
    repository_root: Path,
    current_branch: str | None,
) -> None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(path, f"invalid JSON: {error}")
    if not isinstance(data, dict):
        fail(path, "record root must be a JSON object")

    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        fail(path, f"missing required fields: {', '.join(sorted(missing))}")
    if data["schema_version"] != 1:
        fail(path, "schema_version must be 1")
    if require_string(path, data, "approval_type") != "bounded-batch":
        fail(path, "approval_type must be bounded-batch")
    status = require_string(path, data, "status")
    if status not in ALLOWED_STATUSES:
        fail(path, f"unsupported status: {status}")
    require_string(path, data, "batch_id")
    require_string(path, data, "approved_by")
    require_string(path, data, "approved_scope")
    approved_at = parse_timestamp(path, "approved_at", data["approved_at"])
    expires_at = parse_timestamp(path, "expires_at", data["expires_at"])
    if expires_at <= approved_at:
        fail(path, "expires_at must be after approved_at")
    execution_branch = require_string(path, data, "execution_branch")
    if current_branch == execution_branch and status in {
        "approved_for_execution", "in_progress", "awaiting_post_review",
    } and expires_at <= datetime.now(timezone.utc):
        fail(path, "active execution approval has expired")
    approval_commit = require_string(path, data, "approval_commit")
    if not COMMIT_PATTERN.fullmatch(approval_commit):
        fail(path, "approval_commit must be a 40-character git commit SHA")
    if not execution_branch.startswith("batch/"):
        fail(path, "execution_branch must use the batch/<batch-id> convention")
    try:
        subprocess.run(
            ["git", "merge-base", "--is-ancestor", approval_commit, "HEAD"],
            cwd=repository_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        fail(path, "approval_commit must be an ancestor of the current commit")
    allowed_paths = require_string_list(path, data, "allowed_paths")
    require_string_list(path, data, "allowed_phases")
    require_string_list(path, data, "allowed_operations")
    require_string_list(path, data, "invalidating_triggers")

    issue_ids = require_string_list(path, data, "issue_ids")
    if len(issue_ids) != len(set(issue_ids)):
        fail(path, "issue_ids must be unique")
    for issue_id in issue_ids:
        if not ISSUE_PATTERN.fullmatch(issue_id):
            fail(path, f"invalid Issue ID: {issue_id}")
        matches = list((repository_root / "docs" / "issues").glob(f"{issue_id}-*.md"))
        if len(matches) != 1:
            fail(path, f"expected exactly one Issue file for {issue_id}")

    if not isinstance(data["post_review_required"], bool):
        fail(path, "post_review_required must be boolean")
    if data["post_review_required"] and status == "post_reviewed":
        require_string(path, data, "post_reviewed_by")
        parse_timestamp(path, "post_reviewed_at", data.get("post_reviewed_at"))
        require_string(path, data, "post_review_notes")
    if status == "awaiting_post_review" and not data["post_review_required"]:
        fail(path, "awaiting_post_review requires post_review_required=true")

    if current_branch == execution_branch:
        for changed_path in changed_files_since(repository_root, approval_commit):
            if not is_allowed_path(changed_path, allowed_paths):
                fail(
                    path,
                    f"changed path is outside allowed_paths for {execution_branch}: "
                    f"{changed_path}",
                )


def main() -> int:
    repository_root = Path(__file__).resolve().parents[1]
    current_branch = None
    if len(sys.argv) == 3 and sys.argv[1] == "--branch":
        current_branch = sys.argv[2]
    elif len(sys.argv) != 1:
        print("usage: check-execution-batch-reviews.py [--branch BRANCH]", file=sys.stderr)
        return 2
    review_directory = repository_root / "docs" / "collaboration" / "reviews"
    records = sorted(review_directory.glob(RECORD_GLOB))
    for record in records:
        validate_record(record, repository_root, current_branch)
    print(f"Validated {len(records)} execution-batch review record(s).")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as error:
        print(f"execution-batch review validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)
