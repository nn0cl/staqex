"""O09 test-only evidence reconstruction; never an executable runtime owner."""

import ast
import copy
import hashlib
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/liss_0590"
TYPECHECK = "compiler/staqex/typecheck.py"
OPERATORS = "compiler/staqex/typechecking/operators.py"
CONTEXT = "compiler/staqex/typechecking/operator_context.py"
CLOSED_CARRIER = "tests/test_liss_0588_closed_ownership_red.py"
IMPORT = "from .typechecking.operators import _legacy_check_operator as _operator_check_successor\n"
BLOCK = (
    "    _legacy_check_operator = _operator_check_successor\n\n"
    "    @staticmethod\n"
    "    def _operator_index_type() -> Ty:\n"
    '        return Ty("Meta", "Index", DIMLESS)\n'
)
CONTEXT_HEADER = '''from __future__ import annotations
from typing import Any, Mapping, MutableMapping, MutableSequence, Protocol
from ..ast_nodes import OpExpr, TypeRef, IndexDomain, RevDomain

class OperatorTypeView(Protocol):
    @property
    def kind(self) -> str: ...
    @property
    def payload(self) -> str: ...
    def __str__(self) -> str: ...

class OperatorCheckContext(Protocol):
    env: MutableMapping[str, OperatorTypeView]
    diagnostics: MutableSequence[dict[str, Any]]
    semantic_values: Mapping[str, int]
    float_arrays: Mapping[str, tuple[int, ...]]
    system_registers: Mapping[str, tuple[tuple[str, int], ...]]
    _binder_depth: int
    _active_register_set: str | None
    def _operator_index_type(self) -> OperatorTypeView: ...
    def _check_index_domain_expr(self, domain: IndexDomain | RevDomain) -> None: ...
    def _valid_basis_domain(self, ref: TypeRef) -> bool: ...
    def _valid_index_domain(self, ref: TypeRef) -> bool: ...
    def _ty_from_ref(self, ref: TypeRef) -> OperatorTypeView: ...
    def _check_operator_expr(self, expr: OpExpr) -> None: ...
    def _require_full_rank_coeff(self, expr: OpExpr) -> None: ...
'''
ALGORITHM_IMPORTS = '''from ..ast_nodes import OpBinder, IndexDomain, RevDomain, TypeRef, OpBin, OpIndexed, OpVar, OpLit, OpCall, OpExpr
from .operator_context import OperatorCheckContext, OperatorTypeView
'''


def dump(node):
    return ast.dump(node, include_attributes=False)


def baseline():
    data = (FIXTURES / "baseline.json").read_bytes()
    assert hashlib.sha256(data).hexdigest() == "d965f317a1760db3b4948ab9b21ad18ec9c1e24b06f6bd421c03dcbba8b016f7", "0590 evidence changed"
    return json.loads(data)


def evidence_bytes(name):
    data = (FIXTURES / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == baseline()["evidence_sha256"][name], name
    return data


def original_method():
    node = ast.parse("class TypeChecker:\n" + evidence_bytes("original-operator.txt").decode()).body[0].body[0]
    assert hashlib.sha256(dump(node).encode()).hexdigest() == baseline()["original_ast_sha256"]
    return node


def expected_algorithm():
    """Construct AST-only acceptance shape; never compile/execute this proposal."""
    node = copy.deepcopy(original_method())
    node.args.args[0].annotation = ast.Name(id="OperatorCheckContext", ctx=ast.Load())

    class Types(ast.NodeTransformer):
        replacements = 0

        def visit_Call(self, call):
            if isinstance(call.func, ast.Name) and call.func.id == "Ty":
                assert dump(call) == dump(ast.parse('Ty("Meta", "Index", DIMLESS)', mode="eval").body)
                self.replacements += 1
                return ast.parse("self._operator_index_type()", mode="eval").body
            return self.generic_visit(call)

        def visit_Name(self, name):
            if name.id == "Ty":
                name.id = "OperatorTypeView"
            return name

    change = Types()
    node = change.visit(node)
    assert change.replacements == 2
    return ast.fix_missing_locations(node)


def expected_operators():
    tree = ast.parse(evidence_bytes("original-operators.txt"))
    index = next(i for i, n in enumerate(tree.body) if isinstance(n, ast.FunctionDef))
    tree.body[index:index] = ast.parse(ALGORITHM_IMPORTS).body
    tree.body.append(expected_algorithm())
    return ast.fix_missing_locations(tree)


def without_declaration_docstrings(tree):
    tree = copy.deepcopy(tree)
    for node in [tree, *(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))]:
        if ast.get_docstring(node) is not None:
            node.body = node.body[1:]
    return tree


def assert_successor(directory):
    assert (directory / OPERATORS).is_file(), "operator successor missing"
    assert (directory / CONTEXT).is_file(), "operator context missing"
    actual = without_declaration_docstrings(ast.parse((directory / OPERATORS).read_text()))
    assert dump(actual) == dump(without_declaration_docstrings(expected_operators())), "operator algorithm/entry/import changed"
    actual = without_declaration_docstrings(ast.parse((directory / CONTEXT).read_text()))
    assert dump(actual) == dump(ast.parse(CONTEXT_HEADER)), "operator context contract changed"


def owner(tree):
    return next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "TypeChecker")


def installed(tree):
    return any(isinstance(n, ast.ImportFrom) and n.module == "typechecking.operators" for n in tree.body)


def restore_typechecker_tree(tree, directory=ROOT):
    """Undo only reviewed nodes; preserve mutations to every other original node."""
    tree = copy.deepcopy(tree)
    cls = owner(tree)
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_legacy_check_operator"]
    aliases = [n for n in cls.body if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "_legacy_check_operator" for t in n.targets)]
    factories = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_operator_index_type"]
    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom) and n.module == "typechecking.operators"]
    if imports:
        assert len(imports) == len(aliases) == len(factories) == 1, "duplicate/missing operator wiring"
        assert not methods, "duplicate old operator body"
        assert dump(imports[0]) == dump(ast.parse(IMPORT).body[0]), "wrong operator import"
        expected = ast.parse("class TypeChecker:\n" + BLOCK).body[0].body
        assert dump(aliases[0]) == dump(expected[0]), "wrong bound operator alias"
        assert dump(factories[0]) == dump(expected[1]), "fresh Ty factory changed"
        assert cls.body.index(factories[0]) == cls.body.index(aliases[0]) + 1, "factory position changed"
        assert_successor(directory)
        tree.body.remove(imports[0])
        cls.body.remove(factories[0])
        cls.body[cls.body.index(aliases[0])] = original_method()
    else:
        assert not aliases and not factories and len(methods) == 1, "operator owner missing"
        assert dump(methods[0]) == dump(original_method()), "old operator body changed"
        assert not (directory / CONTEXT).exists(), "two operator ownership shapes mixed"
        assert dump(ast.parse((directory / OPERATORS).read_text())) == dump(ast.parse(evidence_bytes("original-operators.txt")))
    return tree


def readonly_bytes(directory, path):
    data = (directory / path).read_bytes()
    if path == "compiler/staqex/parser.py":
        from tests.liss_0592_guard_support import original_parser_bytes
        return original_parser_bytes(directory)
    if path == TYPECHECK:
        text = data.decode()
        tree = ast.parse(text)
        restore_typechecker_tree(tree, directory)
        if installed(tree):
            assert text.count(IMPORT + "\n") == text.count(BLOCK) == 1, "ambiguous raw-source inverse"
            text = text.replace(IMPORT + "\n", "", 1)
            text = text.replace(BLOCK, evidence_bytes("original-operator.txt").decode(), 1)
            return text.encode()
    elif path == CLOSED_CARRIER:
        original = evidence_bytes(baseline()["carriers"][path])
        assert data in (original, carrier_after(path)), "unapproved closed carrier edit"
        return original
    return data


def carrier_after(path):
    """Exact allowed import/read substitutions; original assertions remain intact."""
    text = evidence_bytes(baseline()["carriers"][path]).decode()
    if path.endswith("0584_repair_boundary_red.py"):
        text = text.replace("import ast\n", "import ast\nfrom tests.liss_0590_guard_support import restore_typechecker_tree\n", 1)
        text = text.replace("def unaffected_digest(tree):\n", "def unaffected_digest(tree):\n    tree = restore_typechecker_tree(tree, ROOT)\n", 1)
    else:
        text = text.replace("import ast\n", "import ast\nfrom tests.liss_0590_guard_support import readonly_bytes\n", 1)
        root_name = "closed.ROOT" if "0588" in path else "capture.ROOT" if "0589" in path else "ROOT"
        old = f"({root_name} / path).read_bytes()"
        assert text.count(old) == 1
        text = text.replace(old, f"readonly_bytes({root_name}, path)", 1)
    return text.encode()


def assert_carriers(directory=ROOT):
    for path in baseline()["carriers"]:
        assert (directory / path).read_bytes() == carrier_after(path), path


def make_shape(destination, extracted, origin=ROOT):
    """Make genuinely distinct pytest temp AST roots, never runtime prototypes."""
    destination = destination.resolve()
    assert destination != ROOT.resolve()
    assert destination.is_relative_to(Path(tempfile.gettempdir()).resolve()), "temporary test roots only"
    original = readonly_bytes(origin, TYPECHECK).decode()
    text = original
    if extracted:
        method = evidence_bytes("original-operator.txt").decode()
        assert text.count(method) == 1
        text = text.replace(method, BLOCK, 1)
        anchor = "@dataclass(frozen=True, slots=True)\nclass Ty:"
        assert text.count(anchor) == 1
        text = text.replace(anchor, IMPORT + "\n" + anchor, 1)
    files = {TYPECHECK: text,
             OPERATORS: ast.unparse(expected_operators()) + "\n" if extracted else evidence_bytes("original-operators.txt").decode()}
    if extracted:
        files[CONTEXT] = CONTEXT_HEADER
    elif (destination / CONTEXT).exists():
        (destination / CONTEXT).unlink()
    for path, contents in files.items():
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents)
    for path in baseline()["carriers"]:
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(carrier_after(path))
    assert installed(ast.parse((destination / TYPECHECK).read_text())) == extracted
    assert (destination / CONTEXT).is_file() == extracted
    assert readonly_bytes(destination, TYPECHECK) == original.encode()
    return destination
