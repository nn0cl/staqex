"""AT-TDD: LISS-0171 Interference prune / support-merge MVP (ADR 0139)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.joint import EPS, Joint, World  # noqa: E402


def test_merge_support_sums_equal_atoms() -> None:
    joint = Joint(
        worlds=[
            World(assign={"x": 1}, amp=0.5 + 0.0j),
            World(assign={"x": 1}, amp=0.5 + 0.0j),
        ]
    )
    merged = joint.merge_support()
    assert len(merged.worlds) == 1
    assert abs(merged.worlds[0].amp - (1.0 + 0.0j)) <= EPS
    assert merged.worlds[0].assign == {"x": 1}


def test_merge_support_prunes_cancelled_amplitude() -> None:
    joint = Joint(
        worlds=[
            World(assign={"x": 0}, amp=1.0 + 0.0j),
            World(assign={"x": 0}, amp=-1.0 + 0.0j),
        ]
    )
    merged = joint.merge_support()
    assert merged.is_vacuum()
    assert len(merged.worlds) == 0


def test_when_keeps_distinct_control_axes() -> None:
    """Correlation law: identical arm values do not merge while ctrl differs."""
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State c = coin()
            State z = mix (c) {
                0 -> 10
                1 -> 10
            }
            measure z
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 10
    assert len(result.eval.joint.worlds) == 2


def test_fn_trace_out_then_merged_identical_arms() -> None:
    """After ADR 0138 drops dead ctrl, identical arms become one support atom."""
    result = run_source(
        """
        package t
        fn merged() -> State<Int> {
            State c = coin()
            State z = mix (c) {
                0 -> 10
                1 -> 10
            }
            return z
        }
        pub fn main() -> Unit {
            State r = merged()
            measure r
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 10
    assert len(result.eval.joint.worlds) == 1
    assert result.eval.joint.worlds[0].assign.get("r") == 10


def test_interfer_cancel_is_vacuum() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State x = |+>
            State y = phase(x, 3.141592653589793)
            State z = interfer(x, y)
            measure z
        }
        """,
        stdout=io.StringIO(),
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.joint.is_vacuum()
    assert result.eval.measure is not None
    assert result.eval.measure.vacuum is True


if __name__ == "__main__":
    test_merge_support_sums_equal_atoms()
    print("PASS test_merge_support_sums_equal_atoms")
    test_merge_support_prunes_cancelled_amplitude()
    print("PASS test_merge_support_prunes_cancelled_amplitude")
    test_when_keeps_distinct_control_axes()
    print("PASS test_when_keeps_distinct_control_axes")
    test_fn_trace_out_then_merged_identical_arms()
    print("PASS test_fn_trace_out_then_merged_identical_arms")
    test_interfer_cancel_is_vacuum()
    print("PASS test_interfer_cancel_is_vacuum")
