#!/usr/bin/env python3
"""Deterministic consistency checks for P1 coverage ledger ↔ Open Topics sync.

Fails CI when Adjudicator-facing docs disagree about typed surface ship status,
Option B completion, or required artifact presence.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]

LEDGER = _REPO / "docs/specs/staqex-v1-language-coverage-ledger.md"
CLAUDE = _REPO / "CLAUDE.md"
PROJECT_CONVENTIONS = _REPO / "docs/collaboration/project-conventions.md"
PERMANENT_OUT = _REPO / "docs/specs/staqex-v1-open-topics-permanent-out.md"
QPU_HONESTY = _REPO / "docs/specs/staqex-v1-qpu-capability-honesty.md"
ADR_0115 = _REPO / "docs/architecture/decision-themes/dec-0002-state-first-semantics-and-measurement.md"
OPEN_WORK = _REPO / "docs/architecture/open-work-register.md"
MISSION = _REPO / "docs/specs/staqex-v1-showcase-mission-lock.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _fail(messages: list[str]) -> None:
    for message in messages:
        print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    errors: list[str] = []

    for path in (
        LEDGER,
        CLAUDE,
        PROJECT_CONVENTIONS,
        PERMANENT_OUT,
        QPU_HONESTY,
        ADR_0115,
        OPEN_WORK,
        MISSION,
    ):
        if not path.is_file():
            errors.append(f"missing required artifact: {path.relative_to(_REPO)}")
    if errors:
        _fail(errors)

    ledger = _read(LEDGER)
    claude = _read(CLAUDE)
    project_conventions = _read(PROJECT_CONVENTIONS)
    open_work = _read(OPEN_WORK)
    mission = _read(MISSION)

    if not re.search(
        r"Typed surface `state x: State<Int>`\s*\|\s*\*\*shipped\*\*",
        ledger,
    ):
        errors.append("ledger §1 must mark Typed surface as **shipped**")

    if not re.search(
        r"Typed surface annotations\s*\|\s*\*\*required\*\*\s*\|\s*\*\*shipped\*\*",
        ledger,
    ):
        errors.append("ledger §3 must mark Typed surface annotations as shipped")

    if "S1 authorize unblocked" not in ledger and "ready for Adjudicator authorize" not in ledger:
        errors.append("ledger gate implication must unblock S1 authorize")

    if "LISS-0129 typed surface **shipped**" not in project_conventions:
        errors.append(
            "project-conventions.md must record LISS-0129 typed surface as shipped"
        )

    if re.search(
        r"Typed surface annotations.*\*\*not shipped\*\*",
        claude,
        flags=re.IGNORECASE,
    ):
        errors.append("CLAUDE.md must not list typed surface as not shipped")

    if "PARSE_ERROR" in claude and "typed surface" in claude.lower():
        # Allow historical mentions only outside Open Topics honesty section.
        open_topics = claude.split("## Current Open Topics", 1)[-1]
        if "PARSE_ERROR" in open_topics and "not shipped" in open_topics.lower():
            errors.append("CLAUDE.md Open Topics must not claim typed surface PARSE_ERROR")

    if "S1 blocked" in open_work and "Showcase S0" in open_work:
        # Narrow: the S0 open-work row must not still claim Option B block.
        for line in open_work.splitlines():
            if "Showcase S0" in line and "S1 blocked" in line:
                errors.append("open-work S0 row still says S1 blocked by Option B")

    if "Open Topics out; F-01" in open_work:
        errors.append("open-work P1 row still says 'Open Topics out' (stale vs Option B complete)")

    if "P1 ledger rows stay" in mission and "provisional" in mission:
        errors.append("mission lock still says P1 ledger rows are provisional")

    if "consume-on-return residuals → LISS-0126+" in ledger:
        errors.append("ledger still points LINEAR residuals at LISS-0126+ (closed in LISS-0133)")

    if errors:
        _fail(errors)

    print("OK — coverage ledger / Open Topics consistency")


if __name__ == "__main__":
    main()
