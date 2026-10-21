"""R06: exact test-only source inverse; never execute proposed repair code."""

import ast
import hashlib
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/liss_0592"
PARSER = "compiler/staqex/parser.py"
REDUCER = '''
    def __reduce__(self):
        """Preserve constructor inputs, independent args and instance state."""
        return (
            _restore_parse_error,
            (type(self), self.message, self.line, self.col, self.args),
            self.__dict__.copy(),
        )
'''
RESTORER = '''def _restore_parse_error(error_type, message, line, col, args):
    """Reconstruct a ParseError without changing its public constructor."""
    error = error_type(message, line, col)
    error.args = args
    return error


'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(tree):
    return ast.dump(tree, include_attributes=False)


def baseline():
    data = (FIXTURES / "baseline.json").read_bytes()
    assert sha(data) == "dfc6c92bc7ca9d5f0a46c181fec1cde0613e1ab35b995100d737ff63d075d45a", "0592 baseline changed"
    return json.loads(data)


def evidence(name):
    data = (FIXTURES / name).read_bytes()
    assert sha(data) == baseline()["evidence_sha256"][name], name
    return data


def nodes(tree):
    owner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ParseError")
    reducers = [n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == "__reduce__"]
    restorers = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_restore_parse_error"]
    return owner, reducers, restorers


def repaired(data):
    _, reducers, restorers = nodes(ast.parse(data))
    return bool(reducers or restorers)


def original_parser_bytes(directory):
    """Only the two approved additions normalize; every other byte stays live."""
    from tests.liss_0591_guard_support import parser_bytes
    text = parser_bytes(directory).decode("utf-8")
    tree = ast.parse(text)
    owner, reducers, restorers = nodes(tree)
    if reducers or restorers:
        assert len(reducers) == len(restorers) == 1, "missing/duplicate serialization owner"
        expected_reducer = ast.parse("class ParseError:\n" + REDUCER).body[0].body[0]
        expected_restorer = ast.parse(RESTORER).body[0]
        assert dump(reducers[0]) == dump(expected_reducer), "reducer contract changed"
        assert dump(restorers[0]) == dump(expected_restorer), "restorer contract changed"
        assert text.count(REDUCER) == text.count(RESTORER) == 1, "ambiguous raw repair inverse"
        owner.body.remove(reducers[0])
        tree.body.remove(restorers[0])
        text = text.replace(REDUCER, "", 1).replace(RESTORER, "", 1)
    assert sha(dump(tree).encode()) == baseline()["parser_ast_sha256"], "unapproved parser AST change"
    assert sha(text.encode()) == baseline()["parser_sha256"], "unapproved parser byte change"
    return text.encode()


def make_shape(destination, repair, origin=ROOT):
    """AST/raw-only pytest root, never a runnable repair implementation."""
    destination = Path(destination).resolve()
    assert destination != ROOT.resolve()
    assert destination.is_relative_to(Path(tempfile.gettempdir()).resolve())
    text = original_parser_bytes(origin).decode()
    if repair:
        anchor = "        self.code = code\n"
        assert text.count(anchor) == 1
        text = text.replace(anchor, anchor + REDUCER, 1)
        anchor = "def _flatten_namespaces("
        assert text.count(anchor) == 1
        text = text.replace(anchor, RESTORER + anchor, 1)
    target = destination / PARSER
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    assert repaired(target.read_bytes()) is repair
    assert original_parser_bytes(destination) == original_parser_bytes(origin)
    return destination


def carrier_after(path):
    text = evidence(baseline()["carriers"][path]).decode()
    if path.endswith("liss_0590_guard_support.py"):
        anchor = "    data = (directory / path).read_bytes()\n"
        assert text.count(anchor) == 1
        text = text.replace(anchor, anchor +
                            '    if path == "compiler/staqex/parser.py":\n'
                            '        from tests.liss_0592_guard_support import original_parser_bytes\n'
                            '        return original_parser_bytes(directory)\n', 1)
    else:
        anchor = "hashlib.sha256((guard.ROOT / path).read_bytes())"
        assert text.count(anchor) == 1
        text = text.replace(anchor, "hashlib.sha256(guard.readonly_bytes(guard.ROOT, path))", 1)
    return text.encode()


def assert_carriers():
    for path in baseline()["carriers"]:
        from tests.liss_0591_guard_support import historical_test_bytes
        assert historical_test_bytes(ROOT, path) == carrier_after(path), path
