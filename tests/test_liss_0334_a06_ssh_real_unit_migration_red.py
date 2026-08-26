"""AT-TDD: LISS-0334 -- migrate A06_topological_edge_memory to real
physical units (WP-0095 work unit 4).

Design decision: docs/issues/LISS-0334-a06-ssh-real-unit-migration.md
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_path, run_path  # noqa: E402

_A06_PATH = str(
    _REPO
    / "examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx"
)


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def test_a06_compiles_and_runs_to_a_real_terminal_measurement() -> None:
    compiled = compile_path(_A06_PATH)
    hard_compile = _hard(compiled.diagnostics)
    assert compiled.ok and not hard_compile, hard_compile

    result = run_path(
        _A06_PATH, settings={"target": "local", "seed": 0}, stdout=io.StringIO()
    )
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)
    assert result.measurements
    assert not result.measurements[0].vacuum
