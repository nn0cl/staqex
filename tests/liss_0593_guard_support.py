"""F06–F09: closed raw projections, never executable production proposals."""

import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/liss_0593"
PREFIX = "compiler/staqex/scientific_semantic/"
LEGACY = PREFIX + "legacy.py"
FINGERPRINT = PREFIX + "fingerprint.py"
BUILDER = PREFIX + "builder.py"
SOURCES = (LEGACY, FINGERPRINT, BUILDER)
CARRIERS = (
    "tests/liss_0590_guard_support.py",
    "tests/liss_0591_guard_support.py",
    "tests/test_liss_0591_ownership_red.py",
)
FUNCTIONS = {
    "semantic_fingerprint": FINGERPRINT,
    "build_inspection": BUILDER,
    "build_rejection": BUILDER,
}
NEW_TESTS = {
    "tests/liss_0593_guard_support.py",
    "tests/test_liss_0593_pure_families_red.py",
    "tests/test_liss_0593_guard_composition_red.py",
}
NEW_FIXTURES = {"tests/fixtures/liss_0593/" + name for name in (
    "baseline.json", "source-legacy.txt", "source-fingerprint.txt",
    "source-builder.txt", "carrier-0.txt", "carrier-1.txt", "carrier-2.txt",
)}
def sha(data):
    return hashlib.sha256(data).hexdigest()


def baseline():
    data = (FIXTURES / "baseline.json").read_bytes()
    assert sha(data) == "97738cc8f552787e61d0d4926db54d02af324683ce82f0cf41561997a8c22e6a", "0593 evidence changed"
    return json.loads(data)


def evidence(path):
    record = baseline()
    filename = (record["sources"] | record["carriers"])[path]
    data = (FIXTURES / filename).read_bytes()
    assert sha(data) == record["evidence_sha256"][filename], filename
    return data


def definition(data, name):
    nodes = [n for n in ast.parse(data).body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(nodes) == 1, (name, "missing/duplicate definition")
    node = nodes[0]
    return b"".join(data.splitlines(keepends=True)[node.lineno - 1:node.end_lineno])


def replace_once(data, old, new):
    assert data.count(old) == 1, "ambiguous raw anchor"
    return data.replace(old, new, 1)


def expected_sources():
    """AST/raw test data only; consumers must never import these proposals."""
    legacy, fingerprint, builder = (evidence(p) for p in SOURCES)
    originals = {name: definition(legacy, name) for name in FUNCTIONS}
    for name, path in FUNCTIONS.items():
        module = "fingerprint" if path == FINGERPRINT else "builder"
        legacy = replace_once(legacy, originals[name], f"from .{module} import {name}\n".encode())
    exports = json.dumps(baseline()["exports"]["compiler.staqex.scientific_semantic.fingerprint"])
    fingerprint = replace_once(fingerprint, b"from . import legacy as _legacy\n",
                               ("import hashlib\nimport json\n\n__all__ = " + exports + "\n").encode())
    fingerprint = replace_once(fingerprint, definition(fingerprint, "semantic_fingerprint"), originals["semantic_fingerprint"])
    builder = replace_once(builder, b"from . import legacy as _legacy\n", b"")
    builder = replace_once(builder, b"    return _legacy.build_scientific_semantic_ir(unit, *args, **kwargs)\n",
                           b"    from . import legacy as _legacy\n\n    return _legacy.build_scientific_semantic_ir(unit, *args, **kwargs)\n")
    for name in ("build_inspection", "build_rejection"):
        builder = replace_once(builder, definition(builder, name), originals[name])
    result = dict(zip(SOURCES, (legacy, fingerprint, builder)))
    for data in result.values():
        ast.parse(data)
    return result


def source_shape(directory):
    directory = Path(directory)
    # Read all real artifacts on every call; cached inventories are not existence.
    actual = {p: (directory / p).read_bytes() for p in SOURCES}
    pre = {p: evidence(p) for p in SOURCES}
    if actual == pre:
        return "pre"
    assert actual == expected_sources(), "unauthorized/mixed semantic source shape"
    return "post"


def readonly_bytes(directory, path):
    path = str(path)
    data = (Path(directory) / path).read_bytes()
    if path in SOURCES:
        source_shape(directory)
        return evidence(path)
    return data


def new_test_paths():
    paths = NEW_TESTS | NEW_FIXTURES
    assert all((ROOT / p).is_file() for p in paths), "0593 test artifact missing"
    return paths


def carrier_after(path):
    """Exact three-carrier proposal; never applied to the working-tree carriers here."""
    data = evidence(path)
    if path == CARRIERS[0]:
        anchor = b"    data = (directory / path).read_bytes()\n"
        dispatch = ("    if path in " + repr(SOURCES) + ":\n"
                    "        from tests.liss_0593_guard_support import readonly_bytes as semantic_bytes\n"
                    "        return semantic_bytes(directory, path)\n").encode()
        return replace_once(data, anchor, anchor + dispatch)
    if path == CARRIERS[1]:
        anchor = b"def readonly_bytes(directory, path):\n"
        dispatch = ("    if path in " + repr(SOURCES) + ":\n"
                    "        from tests.liss_0593_guard_support import readonly_bytes as semantic_bytes\n"
                    "        return semantic_bytes(directory, path)\n").encode()
        data = replace_once(data, anchor, anchor + dispatch)
        data = replace_once(data, b"import ast\n", b"import ast\n" +
                            b"from tests.liss_0593_guard_support import NEW_TESTS as _semantic_tests, NEW_FIXTURES as _semantic_fixtures\n")
        unions = (b"NEW_TESTS = NEW_TESTS | _semantic_tests\n"
                  b"NEW_FIXTURES = NEW_FIXTURES | _semantic_fixtures\n\n\n")
        data = replace_once(data, b"def sha(data):\n", unions + b"def sha(data):\n")
        anchor = b"    data = (Path(directory) / path).read_bytes()\n"
        data = replace_once(data, anchor, anchor +
            b"    from tests.liss_0593_guard_support import historical_carrier_bytes\n"
            b"    data = historical_carrier_bytes(directory, path, data, rejection_message='unapproved carrier change')\n")
        data = replace_once(data, b"    assert actual - old == NEW_TESTS | NEW_FIXTURES,",
            b"    from tests.liss_0593_guard_support import new_test_paths\n"
            b"    assert actual - old == NEW_TESTS | NEW_FIXTURES | new_test_paths(),")
        data = replace_once(data, b"        assert (Path(directory) / path).read_bytes() == carrier_after(path), path",
            b"        from tests.liss_0593_guard_support import historical_carrier_bytes\n"
            b"        assert historical_carrier_bytes(directory, path, (Path(directory) / path).read_bytes()) == carrier_after(path), path")
        return data
    assert path == CARRIERS[2]
    data = replace_once(data, b"guard.sha((guard.ROOT / path).read_bytes()) == expected, path",
                        b"guard.sha(guard.readonly_bytes(guard.ROOT, path)) == expected, path")
    old = data[data.index(b"def test_b06_pure_inverse_has_no_project_import_or_executable_proposal():"):]
    new = b'''def test_b06_pure_inverse_has_no_project_import_or_executable_proposal():
    from tests.liss_0593_guard_support import assert_inverse_closure
    assert_inverse_closure(guard.ROOT)
'''
    return replace_once(data, old, new)


def historical_carrier_bytes(directory, path, data, *, rejection_message="unauthorized carrier edit"):
    assert (Path(directory) / path).read_bytes() == data, "requested carrier missing/changed"
    if path in CARRIERS:
        original = evidence(path)
        assert data in (original, carrier_after(path)), rejection_message
        return original
    return data


def assert_inverse_closure(directory):
    """Only the explicitly accepted pure dependency may cross the 0591 boundary."""
    allowed = "tests.liss_0593_guard_support"
    for relative in (CARRIERS[1], "tests/liss_0593_guard_support.py"):
        tree = ast.parse((Path(directory) / relative).read_bytes())
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                modules = ([n.name for n in node.names] if isinstance(node, ast.Import)
                           else [node.module or ""])
                if isinstance(node, ast.ImportFrom):
                    assert node.level == 0, "relative inverse import"
                for name in modules:
                    if relative == CARRIERS[1] and name == allowed:
                        continue
                    assert name.split(".")[0] in sys.stdlib_module_names, (relative, name)
            if isinstance(node, ast.Call):
                name = (node.func.id if isinstance(node.func, ast.Name)
                        else node.func.attr if isinstance(node.func, ast.Attribute) else "")
                assert name not in {"exec", "eval", "compile", "__import__", "import_module"}, (relative, name)
