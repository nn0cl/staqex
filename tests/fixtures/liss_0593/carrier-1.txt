"""P09/B03: exact raw evidence projections; AST-only shapes are never imported."""

import ast
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/liss_0591"
PARSER = "compiler/staqex/parser.py"
OPERATORS = "compiler/staqex/parsing/operators.py"
CONTEXT = "compiler/staqex/parsing/operator_context.py"
IMPORT = "from .parsing.operators import _legacy_parse_operator_expression as _operator_parse_successor\n"
BLOCK = '''    _legacy_parse_operator_expression = _operator_parse_successor

    @staticmethod
    def _operator_parse_error(message: str, line: int, col: int) -> ParseError:
        return ParseError(message, line, col)

'''
OWNER_IMPORTS = '''from ..ast_nodes import OpAttr, OpCall, OpHop, OpIndexed, OpLit, OpPauli, OpVar
from ..tokens import TokenKind
from .operator_context import OperatorParseContext

'''
OWNER_EXPORTS = '''__all__ = [
    "Any",
    "ParserContext",
    "annotations",
    "parse_operator_expression",
]

'''
CONTEXT_SOURCE = '''"""Narrow, declaration-only operator primary context."""
from __future__ import annotations
from typing import Any, Protocol
from ..ast_nodes import Expr, OpExpr, Span
from ..tokens import Token, TokenKind

class OperatorParseContext(Protocol):
    _prev: Token | None
    def _span(self) -> Span: ...
    def _match(self, *kinds: TokenKind) -> bool: ...
    def _check(self, kind: TokenKind) -> bool: ...
    def _advance(self) -> Token: ...
    def _expect(self, kind: TokenKind) -> Token: ...
    def _peek(self) -> Token: ...
    def _op_expression(self) -> OpExpr | Expr: ...
    def _ket_or_outer(self, token: Token, span: Span) -> Expr: ...
    def _comma_op_expr_items(self, closer: TokenKind) -> list[Any]: ...
    def _algebra_call(self, name: str, items: list[Any], span: Span) -> Expr: ...
    def _op_binder(self, name: str, span: Span) -> OpExpr: ...
    def _operator_parse_error(self, message: str, line: int, col: int) -> Exception: ...
'''
NEW_TESTS = {
    "tests/liss_0591_guard_support.py", "tests/liss_0591_behavior_support.py",
    "tests/test_liss_0591_ownership_red.py", "tests/test_liss_0591_behavior_red.py",
    "tests/test_liss_0591_consumers_red.py", "tests/test_liss_0591_guard_migration_red.py",
}
NEW_FIXTURES = {"tests/fixtures/liss_0591/" + name for name in
                ["baseline.json", "original-primary.txt", "original-operators.txt",
                 *("carrier-%d.txt" % i for i in range(6)), "behavior.json"]}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(tree):
    return ast.dump(tree, include_attributes=False)


def baseline():
    data = (FIXTURES / "baseline.json").read_bytes()
    assert sha(data) == "340bb8054391e2f592709d4511ec24b0ed82e2d3941b4b5aa488cdc91e620d63", "0591 baseline changed"
    return json.loads(data)


def evidence(name):
    data = (FIXTURES / name).read_bytes()
    assert sha(data) == baseline()["evidence_sha256"][name], name
    return data


def original_method():
    node = ast.parse("class Parser:\n" + evidence("original-primary.txt").decode()).body[0].body[0]
    assert sha(dump(node).encode()) == baseline()["original_method_ast"]
    return node


def algorithm_source():
    text = textwrap.dedent(evidence("original-primary.txt").decode())
    assert text.count("raise ParseError(") == 3
    return text.replace("(self):", "(self: OperatorParseContext):", 1).replace(
        "raise ParseError(", "raise self._operator_parse_error(")


def expected_operators():
    algorithm = algorithm_source().encode()
    # E03 permits one final LF removal in the new owner only, not in evidence
    # or the raw facade inverse. Reject a different historical suffix first.
    assert algorithm.endswith(b"\n\n") and not algorithm.endswith(b"\n\n\n"), "original primary EOF changed"
    return (evidence("original-operators.txt") + b"\n" + OWNER_IMPORTS.encode()
            + OWNER_EXPORTS.encode() + algorithm[:-1])


def assert_successor(directory):
    directory = Path(directory)
    assert (directory / OPERATORS).is_file(), "primary successor missing"
    assert (directory / CONTEXT).is_file(), "primary context missing"
    # Preserve the complete algorithm, including original literal/comment bytes.
    assert (directory / OPERATORS).read_bytes() == expected_operators(), "primary owner algorithm/import bytes changed"
    assert (directory / CONTEXT).read_bytes() == CONTEXT_SOURCE.encode(), "primary context changed"


def installed(data):
    tree = ast.parse(data)
    return any(isinstance(n, ast.ImportFrom) and n.module == "parsing.operators" for n in tree.body)


def parser_bytes(directory):
    """Undo extraction only; do not undo or invent the serialization repair."""
    directory = Path(directory)
    text = (directory / PARSER).read_bytes().decode("utf-8")
    tree = ast.parse(text)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Parser")
    methods = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_legacy_parse_operator_expression"]
    aliases = [n for n in cls.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_legacy_parse_operator_expression" for t in n.targets)]
    factories = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_operator_parse_error"]
    if installed(text):
        assert not methods and len(aliases) == len(factories) == 1, "duplicate/missing primary wiring"
        assert_successor(directory)
        assert text.count(IMPORT + "\n") == text.count(BLOCK) == 1, "ambiguous primary raw inverse"
        text = text.replace(IMPORT + "\n", "", 1).replace(BLOCK, evidence("original-primary.txt").decode(), 1)
    else:
        assert len(methods) == 1 and not aliases and not factories, "old primary owner missing"
        assert dump(methods[0]) == dump(original_method()), "old primary method changed"
        assert not (directory / CONTEXT).exists(), "mixed primary shapes"
        # Historical0592 make_shape creates parser-only raw roots. It is not
        # an extracted owner; full production/copy checks still require paths.
        if (directory / OPERATORS).exists():
            assert (directory / OPERATORS).read_bytes() == evidence("original-operators.txt"), "old operators changed"
    repair_manifest = json.loads((ROOT / "tests/fixtures/liss_0592/baseline.json").read_bytes())
    assert sha((ROOT / "tests/fixtures/liss_0592/baseline.json").read_bytes()) == baseline()["test_sha256"]["tests/fixtures/liss_0592/baseline.json"]
    allowed = {baseline()["parser_sha256"], repair_manifest["parser_sha256"]}
    assert sha(text.encode()) in allowed, "unapproved parser byte change"
    return text.encode()


def readonly_bytes(directory, path):
    if path == PARSER:
        return parser_bytes(directory)
    if path == OPERATORS:
        assert (Path(directory) / path).is_file(), "requested operators file missing"
        parser_bytes(directory)
        return evidence("original-operators.txt")
    return (Path(directory) / path).read_bytes()


def parser_context_paths(directory):
    directory = Path(directory)
    if (directory / CONTEXT).exists():
        parser_bytes(directory)
        return {CONTEXT}
    return set()


def production_paths(directory, paths):
    paths = set(paths)
    assert paths - parser_context_paths(directory) == set(baseline()["production_paths"]), "unexpected production path"
    return paths - parser_context_paths(directory)


def copy_parser_dependencies(origin, destination):
    selected = Path(destination) / PARSER
    selected_data = selected.read_bytes() if selected.exists() else (Path(origin) / PARSER).read_bytes()
    for path in (PARSER, OPERATORS, CONTEXT):
        if path == CONTEXT and not installed(selected_data):
            continue
        source = Path(origin) / path
        target = Path(destination) / path
        if source.is_file() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())


def carrier_after(path):
    """Closed substitutions; originals come only from the repaired Git base."""
    text = evidence(baseline()["carriers"][path]).decode()
    if path.endswith("liss_0590_guard_support.py"):
        anchor = "        return original_parser_bytes(directory)\n"
        replacement = anchor + '    if path == "compiler/staqex/parsing/operators.py":\n        from tests.liss_0591_guard_support import readonly_bytes as primary_bytes\n        return primary_bytes(directory, path)\n'
        text = replace_once(text, anchor, replacement)
        text = replace_once(text, "    return destination\n", "    from tests.liss_0591_guard_support import copy_parser_dependencies\n    copy_parser_dependencies(origin, destination)\n    return destination\n")
    elif path.endswith("test_liss_0590_operator_ownership_red.py"):
        text = replace_once(text, "import importlib\n", "import importlib\nfrom tests.liss_0591_guard_support import parser_context_paths\n")
        text = replace_once(text, "<= {guard.CONTEXT}", "<= {guard.CONTEXT} | parser_context_paths(guard.ROOT)")
    elif path.endswith("test_liss_0585_tensor_guard_migration_red.py"):
        text = replace_once(text, '\n\n@pytest.fixture(name="guarded")', '\n    from tests.liss_0591_guard_support import copy_parser_dependencies\n    copy_parser_dependencies(origin, destination)\n\n\n@pytest.fixture(name="guarded")')
    elif path.endswith("liss_0592_guard_support.py"):
        text = replace_once(text, '    text = (Path(directory) / PARSER).read_bytes().decode("utf-8")', '    from tests.liss_0591_guard_support import parser_bytes\n    text = parser_bytes(directory).decode("utf-8")')
        text = replace_once(text, '        assert (ROOT / path).read_bytes() == carrier_after(path), path', '        from tests.liss_0591_guard_support import historical_test_bytes\n        assert historical_test_bytes(ROOT, path) == carrier_after(path), path')
    elif path.endswith("test_liss_0592_boundary_red.py"):
        text = replace_once(text, "import subprocess\n", "import subprocess\nfrom tests import liss_0591_guard_support as primary\n")
        text = replace_once(text, "guard.sha((guard.ROOT / path).read_bytes()) == expected, path", "guard.sha(primary.readonly_bytes(guard.ROOT, path)) == expected, path")
        text = replace_once(text, '    assert actual == set(record["production_paths"])', '    assert primary.production_paths(guard.ROOT, actual) == set(record["production_paths"])')
        text = replace_once(text, "    retained = [p for p in paths", "    paths = primary.historical_test_paths(paths)\n    retained = [p for p in paths")
        text = replace_once(text, 'guard.sha((guard.ROOT / path).read_bytes()) for path in retained', 'guard.sha(primary.historical_test_bytes(guard.ROOT, path)) for path in retained')
    else:
        assert path.endswith("test_liss_0592_guard_migration_red.py")
        text = replace_once(text, "    return destination\n", "    from tests.liss_0591_guard_support import copy_parser_dependencies, make_shape\n    copy_parser_dependencies(repair.ROOT, destination)\n    make_shape(destination, False, origin=repair.ROOT)\n    return destination\n")
    return text.encode()


def replace_once(text, old, new):
    assert text.count(old) == 1, "carrier anchor changed"
    return text.replace(old, new, 1)


def historical_test_bytes(directory, path):
    data = (Path(directory) / path).read_bytes()
    if path in baseline()["carriers"]:
        original = evidence(baseline()["carriers"][path])
        assert data in (original, carrier_after(path)), "unapproved carrier change"
        return original
    return data


def historical_test_paths(paths):
    actual = set(subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', 'tests'], cwd=ROOT, text=True).splitlines())
    old = set(baseline()["test_paths"])
    assert old <= actual, "original test deleted"
    assert actual - old == NEW_TESTS | NEW_FIXTURES, "unexpected/missing new test path"
    return [p for p in paths if p in old]


def assert_carriers(directory=ROOT):
    for path in baseline()["carriers"]:
        assert (Path(directory) / path).read_bytes() == carrier_after(path), path


def make_shape(destination, extracted, origin=ROOT):
    """Write only temporary AST/raw test data; never import it as production."""
    destination = Path(destination).resolve()
    assert destination != ROOT.resolve() and destination.is_relative_to(Path(tempfile.gettempdir()).resolve())
    text = parser_bytes(origin).decode()
    if extracted:
        text = replace_once(text, evidence("original-primary.txt").decode(), BLOCK)
        text = replace_once(text, "class ParseError(Exception):", IMPORT + "\nclass ParseError(Exception):")
    for path, data in {PARSER:text.encode(), OPERATORS:expected_operators() if extracted else evidence("original-operators.txt")}.items():
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    if extracted:
        (destination / CONTEXT).write_bytes(CONTEXT_SOURCE.encode())
    elif (destination / CONTEXT).exists():
        (destination / CONTEXT).unlink()
    assert installed((destination / PARSER).read_bytes()) is extracted
    assert parser_bytes(destination) == parser_bytes(origin)
    return destination
