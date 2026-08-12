"""AT-TDD: LISS-0324 `prepare_selection(n: Int)` quantum selection state
(WP-0093 work unit E, first slice).

  Scenario: prepare_selection produces an equal superposition over all
    2^n selection patterns, before any measurement.
  Scenario: terminal Measure yields one concrete selection pattern,
    reproducibly under the same seed.
  Scenario: candidate identity never crosses into the Kernel --
    prepare_selection's signature is (n: Int) only.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import Call, LitInt, LitString, Span, Var  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelError  # noqa: E402
from compiler.staqex.runtime.joint import Joint  # noqa: E402

_SPAN = Span(line=1, col=1)


def _prepare_selection_call(arg) -> Call:
    return Call(
        callee=Var(name="prepare_selection", span=_SPAN),
        args=[arg],
        span=_SPAN,
    )


def _main(body: str) -> str:
    return f"""
package t
pub fn main() -> Unit {{
{body}
}}
"""


def test_prepare_selection_equal_superposition_over_all_patterns() -> None:
    n = 3
    expr = _prepare_selection_call(LitInt(value=n, span=_SPAN))
    evaluator = Evaluator(seed=0)

    joint = evaluator._bind_call(Joint.unit(), "selection", expr)

    assert len(joint.worlds) == 2**n
    total_mass = sum(abs(world.amp) ** 2 for world in joint.worlds)
    assert abs(total_mass - 1.0) < 1e-9
    expected_mass = 1.0 / (2**n)
    for world in joint.worlds:
        assert "selection" in world.assign
        pattern = world.assign["selection"]
        assert isinstance(pattern, tuple)
        assert len(pattern) == n
        assert set(pattern) <= {0, 1}
        assert abs(abs(world.amp) ** 2 - expected_mass) < 1e-9
    patterns = {world.assign["selection"] for world in joint.worlds}
    assert len(patterns) == 2**n


def test_terminal_measure_yields_one_pattern_reproducibly() -> None:
    src = _main(
        """
    State selection = prepare_selection(3)
    Measure selection
"""
    )
    first = run_source(src, settings={"target": "local", "seed": 0})
    second = run_source(src, settings={"target": "local", "seed": 0})

    assert first.status == "succeeded", first.diagnostics
    assert second.status == "succeeded", second.diagnostics
    assert len(first.measurements) == 1
    assert not first.measurements[0].vacuum
    pattern = first.measurements[0].value
    assert isinstance(pattern, tuple)
    assert len(pattern) == 3
    assert set(pattern) <= {0, 1}
    assert second.measurements[0].value == pattern


def test_prepare_selection_rejects_non_int_argument() -> None:
    expr = _prepare_selection_call(LitString(value="not-a-candidate-list", span=_SPAN))
    evaluator = Evaluator(seed=0)

    try:
        evaluator._bind_call(Joint.unit(), "selection", expr)
        raise AssertionError("expected KernelError for a non-Int prepare_selection argument")
    except KernelError:
        pass
