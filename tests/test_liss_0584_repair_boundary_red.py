"""R07 / approved F05 adoption: protect the untouched repair boundary."""

import ast
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/liss_0584/repair-boundary.json"


def boundary():
    assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == (
        "d0d2c74d0552fd31a6894ea7d2908e4ea506fd639e5d986c2ed40423f3fc4bd3"
    )
    return json.loads(FIXTURE.read_text())


def test_existing_f05_owner_and_readonly_dependencies_are_preserved():
    evidence = boundary()
    assert evidence["base_sha"] == "a287be51da358eed195f836afa21b07286128940"
    assert evidence["adopted_owner"] == "LISS-0584"
    assert evidence["adopted_node"] == (
        "tests/test_liss_0583_static_foreach_successor_red.py::"
        "test_compile_opaque_arithmetic_and_observation_remain_rejected[Int i = q + 1]"
    )
    for path, expected in evidence["readonly_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path


def unaffected_digest(tree):
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "TypeChecker")
    functions = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_infer_binop"]
    assert len(functions) == 1
    # Only this implementation body is the accepted repair location. Its
    # signature/decorators and every other declaration/import/body stay fixed.
    functions[0].body = [ast.Pass()]
    return hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()


def test_typechecker_outside_numeric_inference_is_preserved():
    tree = ast.parse((ROOT / "compiler/staqex/typecheck.py").read_text())
    assert unaffected_digest(tree) == boundary()["unaffected_typecheck_ast"]


@pytest.mark.parametrize("mutation", ("unrelated-body", "numeric-signature", "new-state"))
def test_boundary_detects_unapproved_typechecker_changes(mutation):
    tree = ast.parse((ROOT / "compiler/staqex/typecheck.py").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "TypeChecker")
    if mutation == "unrelated-body":
        fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_check_assign")
        fn.body = [ast.Pass()]
    elif mutation == "numeric-signature":
        fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_infer_binop")
        fn.args.args[-1].arg = "different_input"
    else:
        cls.body.append(ast.parse("shared_state = {}").body[0])
    assert unaffected_digest(tree) != boundary()["unaffected_typecheck_ast"]


def test_boundary_allows_only_numeric_body_change_not_signature():
    tree = ast.parse((ROOT / "compiler/staqex/typecheck.py").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "TypeChecker")
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_infer_binop")
    fn.body = ast.parse("return None").body
    assert unaffected_digest(tree) == boundary()["unaffected_typecheck_ast"]
    # Body permission is not a semantic waiver: R01–R06 still govern its result.
