"""AT-TDD: LISS-0172 Deferred Pushforward MVP (ADR 0140)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ir.dag import lower_source_ast  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_deferred_eligible_main_sets_flag() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State a = coin()
            State b = mix (a) {
                0 -> 10
                1 -> 20
            }
            measure b
        }
        """,
        stdout=io.StringIO(),
        seed=0,
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.deferred_pushforward is True
    assert result.eval.deferred_binds_applied == 2
    assert result.eval.measure is not None
    assert result.eval.measure.value in (10, 20)


def test_inspect_forces_eager_path() -> None:
    result = run_source(
        """
        package t
        pub fn main() -> Unit {
            State a = coin()
            State b = mix (a) {
                0 -> 10
                1 -> 20
            }
            State viewed = inspect(b)
            measure viewed
        }
        """,
        stdout=io.StringIO(),
        seed=0,
    )
    assert result.compile_ok, result.diagnostics
    assert result.eval.deferred_pushforward is False
    assert result.eval.measure is not None
    assert result.eval.measure.value in (10, 20)


def test_deferred_matches_eager_measure_under_same_seed() -> None:
    src_body = """
            State a = coin()
            State b = mix (a) {
                0 -> 10
                1 -> 20
            }
    """
    deferred = run_source(
        f"""
        package t
        pub fn main() -> Unit {{
{src_body}
            measure b
        }}
        """,
        stdout=io.StringIO(),
        seed=42,
    )
    eager = run_source(
        f"""
        package t
        pub fn main() -> Unit {{
{src_body}
            State viewed = inspect(b)
            measure viewed
        }}
        """,
        stdout=io.StringIO(),
        seed=42,
    )
    assert deferred.compile_ok and eager.compile_ok
    assert deferred.eval.deferred_pushforward is True
    assert eager.eval.deferred_pushforward is False
    assert deferred.eval.measure is not None and eager.eval.measure is not None
    assert deferred.eval.measure.value == eager.eval.measure.value


def test_bind_cone_includes_dependencies() -> None:
    from compiler.staqex.ast_nodes import StateBind

    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State a = coin()
            State b = mix (a) { 0 -> 10, 1 -> 20 }
            measure b
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None and compiled.unit.main is not None
    binds = [s for s in compiled.unit.main.body.stmts if isinstance(s, StateBind)]
    measure = compiled.unit.main.body.stmts[-1]
    needed = Evaluator._deferred_bind_cone(binds, measure.expr)
    assert "a" in needed and "b" in needed


def test_dag_lowerer_still_builds_measure_node() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State a = coin()
            measure a
        }
        """
    )
    assert compiled.ok and compiled.unit is not None
    dag = lower_source_ast(compiled.unit)
    assert dag.measure is not None
    assert "coin" in dag.summary()["kinds"]


if __name__ == "__main__":
    test_deferred_eligible_main_sets_flag()
    print("PASS test_deferred_eligible_main_sets_flag")
    test_inspect_forces_eager_path()
    print("PASS test_inspect_forces_eager_path")
    test_deferred_matches_eager_measure_under_same_seed()
    print("PASS test_deferred_matches_eager_measure_under_same_seed")
    test_bind_cone_includes_dependencies()
    print("PASS test_bind_cone_includes_dependencies")
    test_dag_lowerer_still_builds_measure_node()
    print("PASS test_dag_lowerer_still_builds_measure_node")
