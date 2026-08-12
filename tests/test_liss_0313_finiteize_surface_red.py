"""AT-TDD: LISS-0313 finiteize surface (ADR 0185 Lane A).

  Scenario: valid equal-width finiteize yields finite State
    When main binds `State psi = finiteize(0.0, 1.0, 2, 2000, 0)`
    Then compile succeeds and seed-0 run measures without LINEAR discard

  Scenario: invalid n_bins fails closed
    When `finiteize(0.0, 1.0, 0, 10)`
    Then runtime/compile fails closed (no empty silent State)
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.evaluator import KernelError  # noqa: E402


def _main(body: str) -> str:
    return f"""
package t
pub fn main() -> Unit {{
{body}
}}
"""


def test_finiteize_compiles_as_state_bind() -> None:
    src = _main(
        """
    State psi = finiteize(0.0, 1.0, 2, 100, 0)
    Measure psi
"""
    )
    c = compile_source(src)
    hard = [
        d
        for d in c.diagnostics
        if str(d.get("code", "")).startswith("LINEAR")
        or str(d.get("code", "")) in {"PARSE_ERROR", "TYPE_ERROR", "UNKNOWN_NAME"}
    ]
    assert c.ok, c.diagnostics
    assert not hard, hard


def test_finiteize_run_seed_zero_two_bins() -> None:
    src = _main(
        """
    State psi = finiteize(0.0, 1.0, 2, 2000, 0)
    Measure psi
"""
    )
    buf = io.StringIO()
    result = run_source(src, seed=0, stdout=buf)
    assert result.ok, result.diagnostics or buf.getvalue()
    # Binary support: measure yields 0 or 1 bin index
    assert result.eval.measure is not None
    assert result.eval.measure.value in (0, 1)


def test_finiteize_invalid_bins_fail_closed() -> None:
    src = _main(
        """
    State psi = finiteize(0.0, 1.0, 0, 10, 0)
    Measure psi
"""
    )
    c = compile_source(src)
    if not c.ok:
        codes = {d.get("code") for d in c.diagnostics}
        assert codes
        return
    buf = io.StringIO()
    try:
        result = run_source(src, seed=0, stdout=buf)
        if not result.ok:
            return
        raise AssertionError("expected fail-closed for invalid n_bins")
    except KernelError as exc:
        msg = str(exc).lower()
        assert "bin" in msg or "invalid" in msg or "monte" in msg


def test_finiteize_is_prelude_not_user_fn() -> None:
    """finiteize is available without import (prelude combinator)."""
    src = _main(
        """
    State psi = finiteize(0.0, 1.0, 4, 50, 1)
    Measure psi
"""
    )
    c = compile_source(src)
    assert c.ok, c.diagnostics
    buf = io.StringIO()
    result = run_source(src, seed=1, stdout=buf)
    assert result.ok, buf.getvalue()
