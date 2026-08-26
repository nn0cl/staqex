"""AT-TDD: LISS-0347 -- migrate S01_quantum_disaster_response/main_day2_recovery
to real units (WP-0095 work unit 15).

Design decision: docs/issues/LISS-0347-s01-day2-recovery-real-unit-migration.md
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_path, run_path  # noqa: E402

_DAY2_RECOVERY_PATH = str(
    _REPO
    / "examples/showcase/S01_quantum_disaster_response/main_day2_recovery.sqx"
)


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def test_day2_recovery_compiles_and_runs_to_a_real_terminal_measurement() -> None:
    compiled = compile_path(_DAY2_RECOVERY_PATH)
    hard_compile = _hard(compiled.diagnostics)
    assert compiled.ok and not hard_compile, hard_compile

    result = run_path(
        _DAY2_RECOVERY_PATH,
        settings={"target": "local", "seed": 0},
        stdout=io.StringIO(),
    )
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
    assert result.measurements
    assert not result.measurements[0].vacuum
