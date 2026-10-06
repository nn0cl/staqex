"""F05–F08 ownership, dispatch and persistent compatibility contracts."""

import ast
import importlib
from pathlib import Path

import pytest

from compiler.staqex.codegen_qasm import OpenQASM3Generator
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator
from tests.test_liss_0583_static_foreach_behavior_red import loop

ROOT = Path(__file__).resolve().parents[1]
SUCCESSOR = "compiler.staqex.runtime.evaluation.static_foreach"
SOURCE = """
package t
pub fn main() -> Unit {
    QubitRegister<3> reg = system()
    ForEach q in reg { apply(H, q) }
    State<Int> answer = Coin()
    Measure answer
}
"""


def test_successor_has_one_expansion_owner_and_no_state_copy():
    module = importlib.import_module(SUCCESSOR)
    tree = ast.parse(Path(module.__file__).read_text())
    function = module.execute_static_foreach
    assert callable(function) and function.__module__ == SUCCESSOR
    assert not any(isinstance(n, ast.ClassDef) for n in tree.body)
    assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                   and n.func.id in {"Evaluator", "dict", "copy", "deepcopy"} for n in ast.walk(tree))
    assert not any(isinstance(n, ast.Attribute) and n.attr in {"copy", "deepcopy"}
                   for n in ast.walk(tree))
    assert not any(isinstance(n, ast.ImportFrom) and (n.module or "").endswith("evaluator")
                   for n in ast.walk(tree))
    assert not any(isinstance(n, (ast.Assign, ast.AnnAssign)) for n in tree.body)


def test_foreach_body_is_absent_from_evaluator_class():
    tree = ast.parse((ROOT / "compiler/staqex/runtime/evaluator.py").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "_run_foreach" for n in cls.body)


def test_real_installer_mapping_setup_and_runtime_hook_identity():
    module = importlib.import_module(SUCCESSOR)
    from compiler.staqex.runtime.evaluation import compatibility
    installer = compatibility.install_static_foreach_compatibility
    class Target:
        pass
    installer(Target)
    assert Target._run_foreach is module.execute_static_foreach
    assert Evaluator._run_foreach is module.execute_static_foreach
    evaluator = ast.parse((ROOT / "compiler/staqex/runtime/evaluator.py").read_text())
    setups = [n for n in evaluator.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
              and isinstance(n.value.func, ast.Name)
              and n.value.func.id == "_install_static_foreach_compatibility"]
    assert len(setups) == 1 and ast.unparse(setups[0]) == "_install_static_foreach_compatibility(Evaluator)"


def test_successor_uses_live_context_and_threads_joint(recording):
    module = importlib.import_module(SUCCESSOR)
    context, events, _ = recording
    # Fixture patches the currently installed owner. The proposed owner is
    # required to be installed too, so both calls must use that same seam.
    assert Evaluator._run_foreach is module.execute_static_foreach
    assert module.execute_static_foreach(context, 1, loop(body=[])) == 3
    context.static_register_sizes["reg"] = 1
    assert module.execute_static_foreach(context, 4, loop(body=[])) == 5
    assert len(events) == 3


def test_actual_execution_dispatch_reaches_private_hook(monkeypatch):
    from compiler.staqex.runtime.evaluation.execution import execute_legacy_ast_body
    compiled = compile_source(SOURCE)
    assert compiled.ok, compiled.diagnostics
    observed = []
    original = Evaluator._run_foreach
    def record(context, joint, statement):
        observed.append((context, statement))
        return original(context, joint, statement)
    monkeypatch.setattr(Evaluator, "_run_foreach", record)
    evaluator = Evaluator(seed=7)
    result = execute_legacy_ast_body(evaluator, compiled.unit)
    assert len(observed) == 1 and observed[0][0] is evaluator
    assert result.measure is not None


def test_existing_qasm_characterization_and_semantic_gate_order():
    compiled = compile_source(SOURCE)
    assert compiled.ok, compiled.diagnostics
    qasm = OpenQASM3Generator(route=False).generate(compiled.unit)
    gates = [line.split("//", 1)[0].rstrip() for line in qasm.splitlines() if line.startswith("h q[")]
    assert len(gates) == 3
    assert gates == ["h q[0];", "h q[1];", "h q[2];"]


@pytest.mark.parametrize("body", ["Int i = index(q)", "Int i = q + 1", "Measure q", "Snapshot q to stdout"])
def test_compile_opaque_arithmetic_and_observation_remain_rejected(body):
    compiled = compile_source(SOURCE.replace("apply(H, q)", body))
    assert not compiled.ok
    codes = {d.get("code") for d in compiled.diagnostics}
    expected = "FOR_EACH_MEASURE_ERROR" if body.startswith(("Measure", "Snapshot")) else "QPU_CLASSICAL_CONTROL_ERROR"
    assert expected in codes


@pytest.mark.parametrize("name,owner", [
    ("ForEachStmt", "compiler.staqex.ast_nodes"),
    ("MVP_MAX_LOGICAL_QUBITS", "compiler.staqex.static_hilbert"),
])
def test_additional_evaluator_public_reexports_keep_original_identity(name, owner):
    evaluator = importlib.import_module("compiler.staqex.runtime.evaluator")
    assert getattr(evaluator, name) is getattr(importlib.import_module(owner), name)


# Explicit fixture import: pytest discovers it in this module without a broad
# repository conftest or hidden shared state.
from tests.test_liss_0583_static_foreach_behavior_red import recording
