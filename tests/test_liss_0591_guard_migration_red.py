"""P09/B01–B10 exact positives, raw negatives and actual inherited copies."""

import ast
import shutil
import subprocess

import pytest

from tests import liss_0591_guard_support as guard
from tests import liss_0592_guard_support as repair
from tests import liss_0590_guard_support as inherited
from tests import test_liss_0592_guard_migration_red as repair_tests
from tests import test_liss_0590_operator_guard_migration_red as old_migration
from tests import test_liss_0590_operator_ownership_red as old_ownership
from tests import test_liss_0585_tensor_guard_migration_red as tensor


@pytest.mark.parametrize("extracted", [False, True], ids=["primary-pre", "primary-post"])
@pytest.mark.parametrize("typechecker_post", [False, True], ids=["typecheck-pre", "typecheck-post"])
@pytest.mark.parametrize("repaired", [False, True], ids=["repair-pre", "repair-post"])
def test_b03_b07_real_readonly_copy_consumers_cross_eight_distinct_shapes(tmp_path, monkeypatch, extracted, typechecker_post, repaired):
    origin = repair_tests.dependency_root(tmp_path / "origin")
    repair.make_shape(origin, repaired)
    guard.make_shape(origin, extracted, origin=origin)
    before = (origin / guard.PARSER).read_bytes()
    assert guard.installed(before) is extracted
    assert repair.repaired(before) is repaired
    target = repair_tests.dependency_root(tmp_path / "target")
    guard.make_shape(target, extracted, origin=origin)
    inherited.make_shape(target, typechecker_post, origin=origin)
    tensor.copy_guarded_dependencies(origin, target)
    assert (target / guard.PARSER).read_bytes() == before
    assert (target / guard.CONTEXT).exists() is extracted
    assert inherited.installed(ast.parse((target / inherited.TYPECHECK).read_bytes())) is typechecker_post

    monkeypatch.setattr(inherited, "ROOT", origin)
    old_migration.test_o09_real_readonly_carriers_with_inherited_copy_setup(target, monkeypatch)
    assert (target / guard.PARSER).read_bytes() == before
    old_migration.test_o09_real_repair_guard_and_original_mutations(target, monkeypatch)
    monkeypatch.setattr(inherited, "ROOT", target)
    old_ownership.test_o07_original_facade_bytes_and_other_production_are_preserved()
    assert repair.original_parser_bytes(target) == repair.original_parser_bytes(origin)
    if extracted:
        guard.assert_successor(target)


def test_b07_distinct_primary_roots_and_repair_normalization_are_real(tmp_path, monkeypatch):
    pre = guard.make_shape(tmp_path / "pre", False)
    post = guard.make_shape(tmp_path / "post", True)
    assert (pre / guard.PARSER).read_bytes() != (post / guard.PARSER).read_bytes()
    assert not guard.installed((pre / guard.PARSER).read_bytes())
    assert guard.installed((post / guard.PARSER).read_bytes())
    assert guard.parser_bytes(pre) == guard.parser_bytes(post)
    # Actual0592 caller copies context first, validates it, then constructs its
    # historical raw repair shapes without mixing extraction owner state.
    complete = repair_tests.dependency_root(tmp_path / "complete")
    guard.make_shape(complete, True, origin=complete)
    monkeypatch.setattr(repair, "ROOT", complete)
    copied = repair_tests.dependency_root(tmp_path / "repair-copy")
    assert not guard.installed((copied / guard.PARSER).read_bytes())
    assert not (copied / guard.CONTEXT).exists()
    for repaired in (False, True):
        repair.make_shape(copied, repaired, origin=copied)
        assert repair.repaired((copied / guard.PARSER).read_bytes()) is repaired
        repair.original_parser_bytes(copied)


@pytest.mark.parametrize("mutation", ["owner-missing", "context-missing", "owner-literal", "owner-comment", "owner-callback", "owner-order", "context-body", "alias", "factory", "duplicate", "unrelated", "repair", "constructor", "extra-import"])
def test_b09_p09_post_shape_rejects_every_unapproved_owner_wiring_or_repair_change(tmp_path, mutation):
    root = guard.make_shape(tmp_path / "post", True)
    guard.assert_successor(root)
    assert guard.sha(guard.parser_bytes(root)) == guard.baseline()["parser_sha256"]
    path = root / guard.PARSER
    if mutation == "owner-missing":
        (root / guard.OPERATORS).unlink()
    elif mutation == "context-missing":
        (root / guard.CONTEXT).unlink()
    elif mutation in {"owner-literal", "owner-comment", "owner-callback", "owner-order"}:
        path = root / guard.OPERATORS
        data = path.read_bytes()
        changes = {
            "owner-literal": (b'name == "hop"', b'name == "otherhop"'),
            "owner-callback": (b"self._op_binder(name, sp)", b"self._algebra_call(name, [], sp)"),
            "owner-order": (b"tok = self._advance()\n", b"tok = self._peek()\n"),
        }
        changed = data + b'\n# changed\n' if mutation == "owner-comment" else data.replace(*changes[mutation], 1)
        assert changed != data
        path.write_bytes(changed)
    elif mutation == "context-body":
        path = root / guard.CONTEXT
        path.write_bytes(path.read_bytes().replace(b"-> bool: ...", b"-> bool: return True", 1))
    else:
        changes = {
            "alias": (b"_legacy_parse_operator_expression = _operator_parse_successor", b"_legacy_parse_operator_expression = parse_operator_expression"),
            "factory": (b"return ParseError(message, line, col)", b"return ParseError(message, col, line)"),
            "duplicate": (guard.BLOCK.encode(), guard.BLOCK.encode() + guard.evidence("original-primary.txt")),
            "unrelated": (b"def _static_index_endpoint(self):", b"def _static_index_endpoint(self, extra=None):"),
            "repair": (b"self.__dict__.copy()", b"{}"),
            "constructor": (b"super().__init__(message)", b"super().__init__(message, line, col)"),
            "extra-import": (b"class ParseError(Exception):", b"import os\nclass ParseError(Exception):"),
        }
        old, new = changes[mutation]
        assert path.read_bytes().count(old) == 1
        path.write_bytes(path.read_bytes().replace(old, new, 1))
    with pytest.raises(AssertionError):
        guard.parser_bytes(root)
    with pytest.raises(AssertionError):
        inherited.readonly_bytes(root, guard.PARSER)


@pytest.mark.parametrize("extracted,path_name", [(False,guard.PARSER), (True,guard.PARSER), (False,guard.OPERATORS), (True,guard.OPERATORS), (True,guard.CONTEXT)])
@pytest.mark.parametrize("newline", ["whole-crlf", "mixed-crlf", "whole-cr"])
def test_b09_raw_newline_changes_rejected_by_both_real_readers(tmp_path, extracted, path_name, newline):
    root = guard.make_shape(tmp_path / "shape", extracted)
    path = root / path_name
    original = path.read_bytes()
    assert guard.sha(guard.parser_bytes(root)) == guard.baseline()["parser_sha256"]
    changed = original.replace(b"\n", b"\r\n", 1) if newline == "mixed-crlf" else original.replace(b"\n", b"\r\n" if newline == "whole-crlf" else b"\r")
    assert changed != original and guard.dump(ast.parse(changed)) == guard.dump(ast.parse(original))
    path.write_bytes(changed)
    for reader in (guard.parser_bytes, repair.original_parser_bytes):
        with pytest.raises(AssertionError):
            reader(root)


@pytest.mark.parametrize("path", list(guard.baseline()["carriers"]))
def test_b04_b05_each_of_six_carriers_rejects_extra_edits(tmp_path, path):
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(guard.carrier_after(path))
    assert guard.historical_test_bytes(tmp_path, path) == guard.evidence(guard.baseline()["carriers"][path])
    target.write_bytes(target.read_bytes() + b"\n# unapproved carrier bytes\n")
    with pytest.raises(AssertionError, match="unapproved carrier change"):
        guard.historical_test_bytes(tmp_path, path)


@pytest.mark.parametrize("extra", ["compiler/staqex/unexpected.py", "compiler/unexpected.txt"])
def test_b08_production_path_projection_rejects_unexpected_additions(tmp_path, extra):
    root = guard.make_shape(tmp_path / "post", True)
    original = set(guard.baseline()["production_paths"]) | {guard.CONTEXT}
    assert guard.production_paths(root, original) == original - {guard.CONTEXT}
    with pytest.raises(AssertionError, match="unexpected production path"):
        guard.production_paths(root, original | {extra})
    with pytest.raises(AssertionError, match="unexpected production path"):
        guard.production_paths(root, original - {guard.PARSER})


def test_b08_closed_new_test_inventory_rejects_extra_or_missing_paths(monkeypatch):
    old = set(guard.baseline()["test_paths"])
    actual = old | guard.NEW_TESTS | guard.NEW_FIXTURES
    def listing(*args, **kwargs):
        return '\n'.join(sorted(actual)) + '\n'
    monkeypatch.setattr(guard.subprocess, "check_output", listing)
    assert set(guard.historical_test_paths(sorted(actual))) == old
    actual.add("tests/unexpected.py")
    with pytest.raises(AssertionError):
        guard.historical_test_paths(sorted(actual))
    actual.remove("tests/unexpected.py")
    actual.remove(next(iter(old)))
    with pytest.raises(AssertionError):
        guard.historical_test_paths(sorted(actual))


@pytest.mark.parametrize("name", ["baseline.json", "original-primary.txt", "original-operators.txt", "carrier-0.txt", "carrier-3.txt"])
def test_b01_b04_immutable_evidence_mutations_are_rejected(tmp_path, monkeypatch, name):
    copied = tmp_path / "evidence"
    shutil.copytree(guard.FIXTURES, copied)
    monkeypatch.setattr(guard, "FIXTURES", copied)
    (copied / name).write_bytes((copied / name).read_bytes() + b"\n")
    with pytest.raises(AssertionError):
        guard.baseline() if name == "baseline.json" else guard.evidence(name)


def test_b01_p01_fixture_and_inverse_algorithm_match_independent_git_ast():
    data = subprocess.check_output(['git', 'show', guard.baseline()['base'] + ':' + guard.PARSER], cwd=guard.ROOT)
    cls = next(n for n in ast.parse(data).body if isinstance(n, ast.ClassDef) and n.name == 'Parser')
    original = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_legacy_parse_operator_expression')
    proposal = ast.parse(guard.algorithm_source()).body[0]
    proposal.args.args[0].annotation = None
    changed = 0
    for node in ast.walk(proposal):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == '_operator_parse_error':
            assert isinstance(node.func.value, ast.Name) and node.func.value.id == 'self'
            node.func = ast.Name(id='ParseError', ctx=ast.Load())
            changed += 1
    assert changed == 3 and guard.dump(proposal) == guard.dump(original)
    for path, name in guard.baseline()['carriers'].items():
        assert guard.evidence(name) == subprocess.check_output(['git', 'show', guard.baseline()['base'] + ':' + path], cwd=guard.ROOT)


@pytest.mark.parametrize("repaired", [False, True], ids=["repair-pre", "repair-post"])
@pytest.mark.parametrize("extracted", [False, True], ids=["primary-pre", "primary-post"])
@pytest.mark.parametrize("reader", ["0591", "0590"])
def test_r1_named_operators_read_requires_actual_file_on_all_shapes(tmp_path, repaired, extracted, reader):
    base = guard.baseline()["base"] if repaired else guard.baseline()["historical_base"]
    root = tmp_path / "git-root"
    for path in (guard.PARSER, guard.OPERATORS):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(subprocess.check_output(['git', 'show', base + ':' + path], cwd=guard.ROOT))
    guard.make_shape(root, extracted, origin=root)
    assert guard.installed((root / guard.PARSER).read_bytes()) is extracted
    assert repair.repaired((root / guard.PARSER).read_bytes()) is repaired
    read = guard.readonly_bytes if reader == "0591" else inherited.readonly_bytes
    assert read(root, guard.OPERATORS) == guard.evidence("original-operators.txt")
    normalized_parser = guard.parser_bytes(root)
    (root / guard.OPERATORS).unlink()
    with pytest.raises((AssertionError, FileNotFoundError)):
        read(root, guard.OPERATORS)
    if not extracted:
        # A parser-only historical raw root remains valid for0592's inverse;
        # that allowance must not synthesize an explicitly requested owner.
        assert guard.parser_bytes(root) == normalized_parser
        repair.original_parser_bytes(root)


@pytest.mark.parametrize("repaired", [False, True], ids=["repair-pre", "repair-post"])
@pytest.mark.parametrize("mutation", [
    "intact", "missing-export", "wrong-export", "extra-export", "duplicate-export",
    "no-final-lf", "extra-final-lf", "whole-crlf", "mixed-crlf", "whole-cr",
    "old-phase2",
])
def test_e02_e03_e04_e06_exact_owner_exports_and_eof_through_real_readers(tmp_path, repaired, mutation):
    # Start from actual Git, not the live owner that is intentionally Red.
    base = guard.baseline()["base"] if repaired else guard.baseline()["historical_base"]
    root = tmp_path / "git-root"
    for path in (guard.PARSER, guard.OPERATORS):
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(subprocess.check_output(['git', 'show', base + ':' + path], cwd=guard.ROOT))
    expected_parser = (root / guard.PARSER).read_bytes()
    expected_historical = subprocess.check_output([
        'git', 'show', guard.baseline()["historical_base"] + ':' + guard.PARSER,
    ], cwd=guard.ROOT)
    guard.make_shape(root, True, origin=root)
    assert guard.installed((root / guard.PARSER).read_bytes())
    assert repair.repaired((root / guard.PARSER).read_bytes()) is repaired
    path = root / guard.OPERATORS
    original = path.read_bytes()
    exports = b'''__all__ = [
    "Any",
    "ParserContext",
    "annotations",
    "parse_operator_expression",
]

'''
    assert original.count(exports) == 1
    assert original.endswith(b"\n") and not original.endswith(b"\n\n")
    assert original.startswith(guard.evidence("original-operators.txt"))
    readers = [
        ("0591-parser", lambda: guard.parser_bytes(root), expected_parser),
        ("0591-operators", lambda: guard.readonly_bytes(root, guard.OPERATORS), guard.evidence("original-operators.txt")),
        ("0590-parser", lambda: inherited.readonly_bytes(root, guard.PARSER), expected_historical),
        ("0590-operators", lambda: inherited.readonly_bytes(root, guard.OPERATORS), guard.evidence("original-operators.txt")),
        ("0592-parser", lambda: repair.original_parser_bytes(root), expected_historical),
    ]
    for name, read, expected in readers:
        assert read() == expected, name
    if mutation == "intact":
        return
    if mutation == "missing-export":
        changed = original.replace(exports, b"", 1)
    elif mutation == "wrong-export":
        changed = original.replace(b'    "annotations",\n', b'    "TokenKind",\n', 1)
    elif mutation == "extra-export":
        changed = original.replace(b'    "annotations",\n', b'    "annotations",\n    "TokenKind",\n', 1)
    elif mutation == "duplicate-export":
        changed = original.replace(exports, exports + exports, 1)
    elif mutation == "no-final-lf":
        changed = original[:-1]
    elif mutation == "extra-final-lf":
        changed = original + b"\n"
    elif mutation == "whole-crlf":
        changed = original.replace(b"\n", b"\r\n")
    elif mutation == "mixed-crlf":
        changed = original.replace(b"\n", b"\r\n", 1)
    elif mutation == "whole-cr":
        changed = original.replace(b"\n", b"\r")
    else:
        assert mutation == "old-phase2"
        changed = original.replace(exports, b"", 1) + b"\n"
    assert changed != original
    path.write_bytes(changed)
    for name, read, expected in readers:
        with pytest.raises(AssertionError, match="primary owner algorithm/import bytes changed"):
            read()
