"""Phase 1 Red contracts for WP-0174 / LISS-0581 (ADR 0228)."""

from __future__ import annotations

import ast
import importlib
import inspect
import io
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from compiler.staqex.pipeline import compile_source
from compiler.staqex.run import run_source
from compiler.staqex.runtime.joint import Joint, World
from compiler.staqex.runtime.evaluator import Evaluator


FRAMES = ROOT / "compiler/staqex/runtime/evaluation/frames.py"
LIVENESS_IMPORT = "compiler.staqex.runtime.evaluation.liveness"

EXPECTED_LIVENESS_FUNCTIONS = {
    "joint_coord_names",
    "trace_out_dead_fn_locals",
    "main_interproc_trace_eligible",
    "stmts_live_vars",
    "trace_out_dead_caller_coords",
    "expr_has_inspect",
    "expr_free_vars",
}


def _main_stmts(source: str):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None and compiled.unit.main is not None
    return compiled.unit.main.body.stmts


def test_live_caller_coordinate_survives_eligible_library_call() -> None:
    source = """
        package t
        fn id(y: State<Bit>) -> State<Bit> { return y }
        fn combine(a: State<Bit>, b: State<Bit>) -> State<Bit> {
            return a + b
        }
        pub fn main() -> Unit {
            State keep = |1>
            State x = |0>
            State r = id(x)
            State later = combine(keep, r)
            Measure later
        }
        """
    result = run_source(source, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1

    stmts = _main_stmts(source)
    call_index = next(
        index
        for index, stmt in enumerate(stmts)
        if getattr(stmt, "name", None) == "r"
    )
    assert Evaluator._main_interproc_trace_eligible(stmts) is True
    live_out = Evaluator._stmts_live_vars(stmts[call_index + 1 :])
    assert {"keep", "r"} <= live_out, live_out

    joint = Joint(
        worlds=[
            World(
                assign={"keep": 1, "x": 0, "r": 0, "y": 0},
                amp=1.0 + 0.0j,
            )
        ]
    )
    evaluator = Evaluator.__new__(Evaluator)
    retained = evaluator._trace_out_dead_caller_coords(joint, live_out, ["r"])
    coords = set(retained.variables())
    assert {"keep", "r"} <= coords, coords
    assert {"x", "y"}.isdisjoint(coords), coords


def test_inspect_disables_interprocedural_liveness() -> None:
    stmts = _main_stmts(
        """
        package t
        pub fn main() -> Unit {
            State x = Coin()
            State viewed = Inspect(x)
            Measure viewed
        }
        """
    )
    assert Evaluator._main_interproc_trace_eligible(stmts) is False


def test_snapshot_disables_interprocedural_liveness() -> None:
    stmts = _main_stmts(
        """
        package t
        pub fn main() -> Unit {
            State x = Coin()
            Snapshot x to stdout
            Measure x
        }
        """
    )
    assert Evaluator._main_interproc_trace_eligible(stmts) is False


def test_successor_owns_algorithms_and_evaluator_ast_walker_hooks() -> None:
    liveness = importlib.import_module(LIVENESS_IMPORT)
    source = inspect.getsource(liveness)
    tree = ast.parse(source)
    declared = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert EXPECTED_LIVENESS_FUNCTIONS <= declared, sorted(
        EXPECTED_LIVENESS_FUNCTIONS - declared
    )
    assert "runtime.evaluator" not in source
    assert "Evaluator(" not in source
    assert "self.objects" not in source
    assert Evaluator._expr_has_inspect is liveness.expr_has_inspect
    assert Evaluator._expr_free_vars is liveness.expr_free_vars


def test_frames_use_successor_instead_of_duplicate_coordinate_helpers() -> None:
    source = FRAMES.read_text(encoding="utf-8")
    tree = ast.parse(source)
    local_helpers = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    } & {"_joint_coord_names", "_trace_out_dead_fn_locals"}
    assert not local_helpers, sorted(local_helpers)
    assert "joint_coord_names" in source
    assert "trace_out_dead_fn_locals" in source
