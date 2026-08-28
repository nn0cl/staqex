#!/usr/bin/env python3
"""Plan WP-0090 source records; historical deletion is index-driven."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_TAG = "docs/pre-canonicalization-2026-08-03"
MAP_PATH = ROOT / "docs/architecture/documentation-compression-map.md"
SOURCE_ROOTS = {
    "issue": ROOT / "docs/issues",
    "work-plan": ROOT / "docs/work-plans",
    "trace": ROOT / "docs/collaboration/traces",
}
CANONICAL_PATHS = {
    "docs/README.md",
    "docs/architecture/current-decision-register.md",
    "docs/architecture/documentation-canonicalization-policy.md",
    "docs/architecture/open-work-register.md",
}
DESTINATION = {
    "issue": "docs/architecture/open-work-register.md",
    "work-plan": "docs/architecture/open-work-register.md",
    "trace": "docs/architecture/documentation-compression-map.md",
}
UNRESOLVED_WORDS = (
    "open",
    "blocked",
    "proposed",
    "deferred",
    "awaiting",
    "investigation",
    "pending",
    "reopened",
    "residual",
    "follow-up open",
    "remains open",
)
COMPLETED_WORDS = ("complete", "completed", "closed", "merged", "superseded", "done")


@dataclass(frozen=True)
class Candidate:
    kind: str
    path: Path
    reason: str
    classification: str = "index-pointer"


@dataclass(frozen=True)
class ClassificationResult:
    """Conservative, reviewable disposition for one source record."""

    path: str
    classification: str
    reason: str
    candidate: bool


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def all_markdown() -> list[Path]:
    return sorted((ROOT / "docs").rglob("*.md"))


def source_texts() -> dict[Path, str]:
    return {path: path.read_text(encoding="utf-8", errors="replace") for path in all_markdown()}


def identifier(path: Path) -> str:
    match = re.match(r"(LISS-\d+|WP-\d+|ADR[- ]?\d+)", path.stem, re.IGNORECASE)
    return match.group(1).upper().replace("ADR-", "ADR ") if match else ""


def explicit_status(text: str) -> str:
    match = re.search(
        r"(?im)^\s*(?:[-*]\s*)?(?:\|\s*)?status(?:/phase)?\s*(?:\|\s*)?:?\s*\*?\*?([^\n|]+)",
        text,
    )
    return match.group(1).strip().lower() if match else ""


def is_completed(text: str) -> bool:
    status = explicit_status(text)
    return is_completed_status(status)


def has_unresolved_signal(text: str) -> bool:
    """Read only the status field; historical detail is not current status."""
    status = explicit_status(text)
    if not status:
        return True
    if "residual" in status and "triaged" not in status:
        return True
    return any(word in status for word in UNRESOLVED_WORDS)


def is_completed_status(status: str) -> bool:
    """Recognize explicit completion without substring false positives."""

    normalized = re.sub(r"[*_`]+", "", status).strip().lower()
    if not normalized or normalized.startswith(("not ", "incomplete")):
        return False
    return normalized in COMPLETED_WORDS or any(
        normalized.startswith(f"{word} ")
        or normalized.startswith(f"{word}—")
        or normalized.startswith(f"{word}-")
        or normalized.startswith(f"{word}:")
        for word in COMPLETED_WORDS
    )


def classify_records(records: list[dict[str, object]]) -> list[ClassificationResult]:
    """Classify records without changing files or consulting a provider.

    This small pure boundary is intentionally more conservative than the
    historical candidate scan. Evidence and unresolved signals are protected;
    only an unreferenced completed record can be proposed as a candidate.
    """

    results: list[ClassificationResult] = []
    for record in records:
        path = str(record["path"])
        status = str(record.get("status", "")).strip().lower()
        references = [str(value) for value in record.get("referenced_by", [])]
        has_review_evidence = bool(record.get("has_review_evidence", False))
        indexed = bool(record.get("indexed", False))
        canonical = bool(record.get("canonical", False))

        if canonical:
            results.append(
                ClassificationResult(
                    path,
                    "retain-canonical",
                    "current canonical entry or register remains authoritative",
                    False,
                )
            )
        elif indexed:
            results.append(
                ClassificationResult(
                    path,
                    "index-pointer",
                    "already represented by an existing compression-map pointer",
                    False,
                )
            )
        elif references:
            results.append(
                ClassificationResult(
                    path,
                    "retain-evidence",
                    f"referenced by {references[0]}",
                    False,
                )
            )
        elif has_review_evidence:
            results.append(
                ClassificationResult(
                    path,
                    "retain-evidence",
                    "required review or acceptance evidence remains attached",
                    False,
                )
            )
        elif any(word in status for word in UNRESOLVED_WORDS):
            results.append(
                ClassificationResult(
                    path,
                    "unresolved-review",
                    "status remains unresolved and requires human review",
                    False,
                )
            )
        elif is_completed_status(status):
            results.append(
                ClassificationResult(
                    path,
                    "index-pointer",
                    "completed record has no supplied current evidence reference",
                    True,
                )
            )
        else:
            results.append(
                ClassificationResult(
                    path,
                    "unresolved-review",
                    "status is missing or not safely classified",
                    False,
                )
            )
    return results


def render_classification_report(records: list[dict[str, object]]) -> str:
    """Render every disposition for human review without changing files."""

    classifications = classify_records(records)
    return "\n".join(
        f"{result.classification}\t{result.path}\treason={result.reason}"
        for result in classifications
    )


def is_pointer_stub(text: str) -> bool:
    return "**historical — compacted**" in text


def batch_work_plan_ids() -> set[str]:
    result: set[str] = set()
    for path in (ROOT / "docs/collaboration/reviews").glob("execution-batch-*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        work_plan_id = data.get("work_plan_id")
        if isinstance(work_plan_id, str):
            result.add(work_plan_id)
    return result


def batch_issue_ids() -> set[str]:
    result: set[str] = set()
    for path in (ROOT / "docs/collaboration/reviews").glob("execution-batch-*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for issue_id in data.get("issue_ids", []):
            if isinstance(issue_id, str):
                result.add(issue_id)
    return result


def candidates() -> list[Candidate]:
    texts = source_texts()
    records = _classification_records(texts)
    classifications = classify_records(records)
    by_path = {str(record["path"]): record for record in records}
    result: list[Candidate] = []
    for classification in classifications:
        if not classification.candidate:
            continue
        record = by_path[classification.path]
        result.append(
            Candidate(
                str(record["kind"]),
                ROOT / classification.path,
                classification.reason,
                classification.classification,
            )
        )
    return result


def baseline_commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", f"{BASELINE_TAG}^{{commit}}"], cwd=ROOT, text=True
    ).strip()


def title(text: str, path: Path) -> str:
    match = re.search(r"(?m)^#\s+(.+)$", text)
    return match.group(1).strip() if match else path.stem


def relative_link(path: Path, target: str) -> str:
    return Path(target).relative_to(path.parent.relative_to(ROOT)).as_posix() if False else target


def stub(row: Candidate, source_commit: str, original: str) -> str:
    if row.kind in {"issue", "work-plan"}:
        adr_link = "../architecture/decision-themes/dec-0007-documentation-and-decision-records.md"
        destination_link = "../architecture/open-work-register.md"
    else:
        adr_link = "../../architecture/decision-themes/dec-0007-documentation-and-decision-records.md"
        destination_link = "../../architecture/documentation-compression-map.md"
    return "\n".join(
        [
            f"# {title(original, row.path)}",
            "",
            "| Field | Value |",
            "|---|---|",
            "| Status | **historical — compacted** |",
            f"| Canonical rule | [ADR 0187]({adr_link}) |",
            f"| Current meaning | [canonical destination]({destination_link}) |",
            f"| Original source commit | `{source_commit}` |",
            f"| Baseline tag | `{BASELINE_TAG}` |",
            f"| Original path | `{relative(row.path)}` |",
            f"| Recovery | `git show {BASELINE_TAG}:{relative(row.path)}` |",
            "",
            "This historical record remains at its stable path as a pointer. The",
            "ADR/specification and current register are the source of truth.",
            "",
        ]
    )


def inventory() -> tuple[list[str], list[Path]]:
    before = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASELINE_TAG, "docs"], cwd=ROOT, text=True
    ).splitlines()
    after = [path for path in (ROOT / "docs").rglob("*") if path.is_file()]
    return before, after


def count(paths: list[str] | list[Path], prefix: str) -> int:
    return sum(1 for path in paths if str(path).startswith(prefix))


def previous_records(section_name: str, classification: str, skip_existing: bool) -> list[Candidate]:
    if not MAP_PATH.exists():
        return []
    result: list[Candidate] = []
    in_section = False
    for line in MAP_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if line == section_name:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        match = re.match(r"\| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| `([^`]+)` \| (.+) \|$", line)
        if not match:
            continue
        path = ROOT / match.group(1)
        if skip_existing and path.exists():
            continue
        kind = "issue" if "/issues/" in match.group(1) else "work-plan" if "/work-plans/" in match.group(1) else "trace"
        if match.group(5) != classification:
            continue
        result.append(Candidate(kind, path, match.group(6)))
    return result


def previous_removed() -> list[Candidate]:
    return previous_records("## Removed records", "extract-and-remove", True)


def previous_compacted() -> list[Candidate]:
    return previous_records("## Compacted records", "compact-pointer", False)


def indexed_deleted_paths() -> list[Path]:
    """Read deletion targets from the central map without scanning active records."""
    if not MAP_PATH.exists():
        return []
    result: list[Path] = []
    for line in MAP_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(
            r"\| `([^`]+)` \| `[^`]+` \| `[^`]+` \| `[^`]+` \| `index-pointer` \|",
            line,
        )
        if match:
            result.append(ROOT / match.group(1))
    return result


def _record_references(path: Path, texts: dict[Path, str]) -> list[str]:
    """Find conservative references to a record in current documentation."""

    record_id = identifier(path)
    if not record_id:
        return []
    return [
        relative(other)
        for other, text in texts.items()
        if other != path and record_id in text
    ]


def _record_has_review_evidence(path: Path, texts: dict[Path, str]) -> bool:
    """Treat review packets and execution batches as retained evidence."""

    record_id = identifier(path)
    if not record_id:
        return False
    if record_id in batch_issue_ids() or record_id in batch_work_plan_ids():
        return True
    return any(
        _is_review_path(other)
        and record_id in text
        for other, text in texts.items()
    )


def _is_review_path(path: Path) -> bool:
    """Recognize review evidence from a repository-relative path."""

    path_text = path.as_posix()
    if path.is_absolute():
        try:
            path_text = relative(path)
        except ValueError:
            return False
    return path_text.startswith("docs/collaboration/reviews/")


def _classification_records(texts: dict[Path, str]) -> list[dict[str, object]]:
    indexed = {relative(path) for path in indexed_deleted_paths()}
    records: list[dict[str, object]] = []
    seen: set[Path] = set()
    for kind, root in SOURCE_ROOTS.items():
        for path in sorted(root.glob("*.md")):
            seen.add(path)
            text = texts[path]
            records.append(
                {
                    "path": relative(path),
                    "kind": kind,
                    "status": explicit_status(text),
                    "referenced_by": _record_references(path, texts),
                    "has_review_evidence": _record_has_review_evidence(path, texts),
                    "indexed": relative(path) in indexed,
                    "canonical": relative(path) in CANONICAL_PATHS,
                }
            )
    for canonical_path in sorted(ROOT / path for path in CANONICAL_PATHS):
        if not canonical_path.exists() or canonical_path in seen:
            continue
        text = texts[canonical_path]
        records.append(
            {
                "path": relative(canonical_path),
                "kind": "canonical",
                "status": explicit_status(text),
                "referenced_by": _record_references(canonical_path, texts),
                "has_review_evidence": _record_has_review_evidence(canonical_path, texts),
                "indexed": relative(canonical_path) in indexed,
                "canonical": True,
            }
        )
    return records


def rewrite_deleted_links(paths: set[Path]) -> int:
    pattern = re.compile(r"(\]\()([^()\s]+)(#[^)]*)?(\))")
    changed = 0
    for page in all_markdown():
        if page in paths or page == MAP_PATH:
            continue
        original = page.read_text(encoding="utf-8", errors="replace")
        destination = os.path.relpath(MAP_PATH, page.parent).replace(os.sep, "/")

        def replace(match: re.Match[str]) -> str:
            target = match.group(2)
            if "://" in target or target.startswith("mailto:"):
                return match.group(0)
            return (
                f"]({destination})"
                if (page.parent / target).resolve() in paths
                else match.group(0)
            )

        updated = pattern.sub(replace, original)
        if updated != original:
            page.write_text(updated, encoding="utf-8")
            changed += 1
    return changed


def render_map(compacted: list[Candidate], removed: list[Candidate], commit: str) -> str:
    before, after = inventory()
    lines = [
        "# Documentation compression map", "",
        "This file is generated and updated as part of WP-0090. It is the recoverability",
        "index for ADR, Issue, Work Plan, and Trace source records compacted or removed",
        "from the current tree.", "", "## Baseline", "",
        "| Field | Value |", "|---|---|", f"| Tag | `{BASELINE_TAG}` |",
        f"| Baseline commit | `{commit}` |", "| Recovery command | `git show <source_tag>:<source_path>` |", "",
        "## Inventory delta", "", "| Area | Before (baseline) | After this batch | Delta |", "|---|---:|---:|---:|",
        f"| All `docs/` files | {len(before)} | {len(after)} | {len(after) - len(before):+d} |",
        f"| Markdown files | {sum(path.endswith('.md') for path in before)} | {sum(path.suffix == '.md' for path in after)} | {sum(path.suffix == '.md' for path in after) - sum(path.endswith('.md') for path in before):+d} |",
        f"| ADRs | {count(before, 'docs/architecture/adr/')} | {count(after, str(ROOT / 'docs/architecture/adr/'))} | {count(after, str(ROOT / 'docs/architecture/adr/')) - count(before, 'docs/architecture/adr/'):+d} |",
        f"| Issues | {count(before, 'docs/issues/')} | {count(after, str(ROOT / 'docs/issues/'))} | {count(after, str(ROOT / 'docs/issues/')) - count(before, 'docs/issues/'):+d} |",
        f"| Work Plans | {count(before, 'docs/work-plans/')} | {count(after, str(ROOT / 'docs/work-plans/'))} | {count(after, str(ROOT / 'docs/work-plans/')) - count(before, 'docs/work-plans/'):+d} |",
        f"| Traces | {count(before, 'docs/collaboration/traces/')} | {count(after, str(ROOT / 'docs/collaboration/traces/'))} | {count(after, str(ROOT / 'docs/collaboration/traces/')) - count(before, 'docs/collaboration/traces/'):+d} |",
        "", "## Compacted records", "", "| source_path | source_commit | source_tag | destination | classification | reason |", "|---|---|---|---|---|---|",
    ]
    for row in compacted:
        lines.append(f"| `{relative(row.path)}` | `{commit}` | `{BASELINE_TAG}` | `{DESTINATION[row.kind]}` | `compact-pointer` | {row.reason} |")
    lines.extend(["", "## Removed records", "", "| source_path | source_commit | source_tag | destination | classification | reason |", "|---|---|---|---|---|---|"])
    for row in removed:
        lines.append(f"| `{relative(row.path)}` | `{commit}` | `{BASELINE_TAG}` | `{DESTINATION[row.kind]}` | `extract-and-remove` | {row.reason} |")
    lines.extend(["", "## Unresolved review", "", "Protected, active, or ambiguous records remain at their original paths and are not silently compacted.", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="deprecated; pointer stubs are no longer created")
    parser.add_argument("--delete-indexed", action="store_true", help="delete only records already indexed as index-pointer")
    args = parser.parse_args()
    if args.apply:
        parser.error("--apply is retired; use the central map and --delete-indexed")
    if args.delete_indexed:
        paths = {path for path in indexed_deleted_paths() if path.exists()}
        for path in paths:
            subprocess.run(
                ["git", "cat-file", "-e", f"{BASELINE_TAG}:{relative(path)}"],
                cwd=ROOT,
                check=True,
            )
        changed = rewrite_deleted_links(paths)
        for path in sorted(paths):
            path.unlink()
        print(f"deleted={len(paths)} links_rewritten={changed}")
        return 0
    rows = candidates()
    texts = source_texts()
    records = _classification_records(texts)
    commit = baseline_commit()
    print(f"baseline={BASELINE_TAG} commit={commit}")
    report = render_classification_report(records)
    if report:
        print(report)
    print(f"candidate_count={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
