#!/usr/bin/env python3
"""Submit the companion program via ``submit_source`` / ``JobResult`` (LISS-0022)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import submit_source  # noqa: E402

_HERE = Path(__file__).parent
_SOURCE = (_HERE / "main_host_job.sqx").read_text(encoding="utf-8")


def main() -> int:
    job = submit_source(_SOURCE, settings={"target": "local", "seed": 0})
    result = job.result()
    print(f"status={result.status}")
    if result.measurements:
        print(f"Measure={result.measurements[0].value}")
    if result.status != "succeeded":
        for diagnostic in result.diagnostics:
            print(diagnostic, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
