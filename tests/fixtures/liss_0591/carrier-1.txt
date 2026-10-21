"""O01/O06/O07: independent structural Reds and immutable outside boundary."""

import ast
import hashlib
import importlib

from compiler.staqex.typecheck import TypeChecker, Ty
from tests import liss_0590_guard_support as guard


def test_o01_sole_successor_owns_exact_original_algorithm():
    guard.assert_successor(guard.ROOT)


def test_o01_old_class_body_is_absent_with_exact_alias_and_factory():
    tree = ast.parse((guard.ROOT / guard.TYPECHECK).read_text())
    cls = guard.owner(tree)
    assert not any(isinstance(n, ast.FunctionDef) and n.name == "_legacy_check_operator" for n in cls.body), "operator body still owned by facade"
    assert guard.installed(tree), "private successor import missing"
    restored = guard.restore_typechecker_tree(tree)
    assert hashlib.sha256(guard.dump(restored).encode()).hexdigest() == guard.baseline()["typecheck_ast"]


def test_o06_both_hooks_are_ordinary_bound_successor_aliases():
    module = importlib.import_module("compiler.staqex.typechecking.operators")
    algorithm = getattr(module, "_legacy_check_operator", None)
    assert callable(algorithm), "private operator algorithm not extracted"
    checker = TypeChecker()
    for name in ("_legacy_check_operator", "_check_operator_expr"):
        assert getattr(TypeChecker, name) is algorithm
        method = getattr(checker, name)
        assert method.__self__ is checker and method.__func__ is algorithm
    assert algorithm is not module.check_operator_expr


def test_o06_factory_is_static_and_returns_fresh_actual_ty():
    assert isinstance(TypeChecker.__dict__.get("_operator_index_type"), staticmethod), "fresh Ty factory missing"
    a, b = TypeChecker._operator_index_type(), TypeChecker()._operator_index_type()
    assert type(a) is type(b) is Ty and a == b and a is not b
    assert (a.kind, a.payload) == ("Meta", "Index")


def test_o07_original_facade_bytes_and_other_production_are_preserved():
    evidence = guard.baseline()
    assert hashlib.sha256(guard.readonly_bytes(guard.ROOT, guard.TYPECHECK)).hexdigest() == evidence["typecheck_sha256"]
    for path, expected in evidence["readonly_sha256"].items():
        assert hashlib.sha256(guard.readonly_bytes(guard.ROOT, path)).hexdigest() == expected, path
    paths = {str(p.relative_to(guard.ROOT)) for p in (guard.ROOT / "compiler").rglob("*.py")}
    assert paths - set(evidence["production_paths"]) <= {guard.CONTEXT}
    assert set(evidence["production_paths"]) <= paths


def test_o07_previous_real_public_exports_remain_available():
    for name, original in guard.baseline()["public_exports"].items():
        module = importlib.import_module(name)
        actual = set(module.__all__ if hasattr(module, "__all__") else (n for n in vars(module) if not n.startswith("_")))
        assert set(original) <= actual, name


def test_o09_exact_four_carriers_and_pinned_original_evidence():
    guard.assert_carriers()
    for name in guard.baseline()["evidence_sha256"]:
        guard.evidence_bytes(name)
