"""H08/H09 four independent structural Red contracts."""

import ast
import importlib
from pathlib import Path

from compiler.staqex.runtime.evaluator import Evaluator
from tests import liss_0586_guard_support as host

ROOT = Path(__file__).resolve().parents[1]


def successor():
    path = ROOT / host.SUCCESSOR
    assert path.is_file(), "Host coefficient successor not implemented"
    return importlib.import_module("compiler.staqex.runtime.evaluation.host_coefficients")


def test_h08_stateless_successor_and_narrow_context():
    module = successor()
    assert module.resolve_host_coefficient_arrays.__module__ == module.__name__
    host.assert_successor_algorithm(Path(module.__file__).read_text())


def test_h08_old_body_absent():
    tree = ast.parse((ROOT / "compiler/staqex/runtime/evaluator.py").read_text())
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Evaluator")
    assert not any(isinstance(n, ast.FunctionDef) and n.name == host.METHOD for n in owner.body)


def test_h08_exact_installer_and_live_private_identity():
    module = successor()
    compatibility = importlib.import_module("compiler.staqex.runtime.evaluation.compatibility")
    class Target:
        pass
    getattr(compatibility, host.INSTALLER)(Target)
    assert getattr(Target, host.METHOD) is module.resolve_host_coefficient_arrays
    assert getattr(Evaluator, host.METHOD) is module.resolve_host_coefficient_arrays
    tree = ast.parse((ROOT / "compiler/staqex/runtime/evaluator.py").read_text())
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom)
               and any(a.name == host.INSTALLER for a in n.names)]
    assert len(imports) == 1 and imports[0].module == "evaluation.compatibility" and imports[0].level == 1
    assert [(a.name, a.asname) for a in imports[0].names] == [(host.INSTALLER, host.PRIVATE)]
    setups = [n for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
              and isinstance(n.value.func, ast.Name) and n.value.func.id == host.PRIVATE]
    assert len(setups) == 1 and host.dump(setups[0]) == host.dump(ast.parse(f"{host.PRIVATE}(Evaluator)").body[0])


def test_h09_actual_algorithm_matches_immutable_original():
    path = ROOT / host.SUCCESSOR
    assert path.is_file(), "Host algorithm not moved"
    host.assert_successor_algorithm(path.read_text())
