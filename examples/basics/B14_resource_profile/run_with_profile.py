#!/usr/bin/env python3
"""Load ``staqex.toml`` and run the companion program with a resource budget check."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.resource_profile import (  # noqa: E402
    estimate_simulator_resources,
    load_resource_profile,
)
from compiler.staqex.run import run_source  # noqa: E402

_HERE = Path(__file__).parent
_SOURCE = (_HERE / "main_resource_profile.sqx").read_text(encoding="utf-8")


def main() -> int:
    profile = load_resource_profile(None, _HERE)
    if profile.diagnostics:
        for diagnostic in profile.diagnostics:
            print(f"{diagnostic['code']}: {diagnostic['message']}", file=sys.stderr)
        return 1

    estimate = estimate_simulator_resources("StateVector", logical_qubits=1)
    result = run_source(
        _SOURCE,
        seed=0,
        stdout=io.StringIO(),
        resource_profile=profile,
        resource_estimate=estimate,
    )
    for diagnostic in result.diagnostics:
        code = diagnostic.get("code", "")
        if code:
            print(f"{code}: {diagnostic.get('message', '')}")

    if not result.compile_ok:
        return 1
    measured = result.eval.measure
    if measured is None:
        return 1
    print(f"Measure={measured.value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
