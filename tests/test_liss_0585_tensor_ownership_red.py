"""T07–T09 structural Red: distinct ownership, identity and algorithm gaps."""

import ast
import importlib
from pathlib import Path

from compiler.staqex.runtime.evaluator import Evaluator
from tests.liss_0585_guard_support import assert_successor_algorithm

ROOT = Path(__file__).resolve().parents[1]
SUCCESSOR = "compiler.staqex.runtime.evaluation.tensor_binding"


def test_t07_successor_owns_only_stateless_tensor_body():
    module = importlib.import_module(SUCCESSOR)
    assert module.bind_tensor.__module__ == SUCCESSOR
    tree = ast.parse(Path(module.__file__).read_text())
    assert not any(isinstance(n, ast.ClassDef) for n in tree.body)
    assert not any(isinstance(n, (ast.Assign, ast.AnnAssign)) for n in tree.body)
    assert not any(isinstance(n, ast.ImportFrom) and (n.module or "").endswith("evaluator")
                   for n in ast.walk(tree))
    assert not any(isinstance(n, ast.Import) and any(a.name.endswith("evaluator") for a in n.names)
                   for n in ast.walk(tree))


def test_t07_old_body_is_absent_from_evaluator():
    tree = ast.parse((ROOT / "compiler/staqex/runtime/evaluator.py").read_text())
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "_bind_tensor" for n in owner.body)


def test_t07_installer_setup_and_runtime_hook_are_exact_successor_identity():
    module = importlib.import_module(SUCCESSOR)
    compatibility = importlib.import_module("compiler.staqex.runtime.evaluation.compatibility")

    class Target:
        pass

    compatibility.install_tensor_binding_compatibility(Target)
    assert Target._bind_tensor is module.bind_tensor
    assert Evaluator._bind_tensor is module.bind_tensor
    tree = ast.parse((ROOT / "compiler/staqex/runtime/evaluator.py").read_text())
    setups = [n for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
              and isinstance(n.value.func, ast.Name) and n.value.func.id == "_install_tensor_binding_compatibility"]
    assert len(setups) == 1
    assert ast.unparse(setups[0]) == "_install_tensor_binding_compatibility(Evaluator)"


def test_t09_actual_successor_algorithm_is_original_except_declared_ownership_changes():
    path = ROOT / "compiler/staqex/runtime/evaluation/tensor_binding.py"
    assert path.is_file(), "tensor successor not implemented"
    assert_successor_algorithm(path.read_text())
