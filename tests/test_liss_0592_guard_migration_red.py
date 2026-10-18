"""R06: real inherited guards on distinct Parser/TypeChecker AST-only roots."""

import ast
import json
import shutil

import pytest

from tests import liss_0592_guard_support as repair
from tests import liss_0590_guard_support as inherited
from tests import test_liss_0590_operator_guard_migration_red as old_migration
from tests import test_liss_0590_operator_ownership_red as old_ownership
from tests import test_liss_0585_tensor_guard_migration_red as tensor


def dependency_root(destination):
    """Copy only real manifest closures; these roots are never imported."""
    paths = set(repair.baseline()["production_paths"])
    paths.update(tensor.repair.boundary()["readonly_sha256"])
    paths.update(inherited.baseline()["readonly_sha256"])
    for number in (587, 588, 589):
        manifest = f"tests/fixtures/liss_0{number}/readonly-boundary.json"
        paths.add(manifest)
        paths.update(json.loads((repair.ROOT / manifest).read_text())["readonly_sha256"])
    for path in paths:
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repair.ROOT / path, target)
    return destination


@pytest.mark.parametrize("parser_repaired", [False, True], ids=["parser-pre", "parser-post"])
@pytest.mark.parametrize("typechecker_post", [False, True], ids=["typecheck-pre", "typecheck-post"])
def test_r06_real_readonly_and_copy_consumers_cross_both_distinct_shapes(tmp_path, monkeypatch, parser_repaired, typechecker_post):
    origin = dependency_root(tmp_path / "origin")
    repair.make_shape(origin, parser_repaired)
    target = dependency_root(tmp_path / "target")
    repair.make_shape(target, parser_repaired)
    before = (target / repair.PARSER).read_bytes()

    # Real inherited helper must not silently overwrite the selected Parser.
    tensor.copy_guarded_dependencies(origin, target)
    assert (target / repair.PARSER).read_bytes() == before
    inherited.make_shape(target, typechecker_post)
    assert repair.repaired((target / repair.PARSER).read_bytes()) is parser_repaired
    assert inherited.installed(ast.parse((target / inherited.TYPECHECK).read_text())) is typechecker_post

    monkeypatch.setattr(inherited, "ROOT", origin)
    old_migration.test_o09_real_readonly_carriers_with_inherited_copy_setup(target, monkeypatch)
    assert (target / repair.PARSER).read_bytes() == before
    assert repair.original_parser_bytes(target) == repair.original_parser_bytes(repair.ROOT)
    old_migration.test_o09_real_repair_guard_and_original_mutations(target, monkeypatch)

    monkeypatch.setattr(inherited, "ROOT", target)
    old_ownership.test_o07_original_facade_bytes_and_other_production_are_preserved()


def test_r06_parser_pre_and_post_are_really_distinct(tmp_path):
    pre = repair.make_shape(tmp_path / "pre", False)
    post = repair.make_shape(tmp_path / "post", True)
    assert not repair.repaired((pre / repair.PARSER).read_bytes())
    assert repair.repaired((post / repair.PARSER).read_bytes())
    assert (pre / repair.PARSER).read_bytes() != (post / repair.PARSER).read_bytes()
    assert repair.original_parser_bytes(pre) == repair.original_parser_bytes(post)


@pytest.mark.parametrize("mutation", [
    "constructor", "grammar", "reducer-args", "restorer-args", "state",
    "extra-import", "extra-state", "missing-helper", "duplicate", "comment",
])
def test_r06_inverse_rejects_unapproved_changes(tmp_path, mutation):
    root = repair.make_shape(tmp_path / "post", True)
    path = root / repair.PARSER
    text = path.read_text()
    changes = {
        "constructor": ('super().__init__(message)', 'super().__init__(message, line, col)'),
        "grammar": ('name == "hop"', 'name == "otherhop"'),
        "reducer-args": ('self.line, self.col, self.args', 'self.col, self.line, self.args'),
        "restorer-args": ('error.args = args', 'error.args = (message,)'),
        "state": ('self.__dict__.copy()', '{}'),
        "extra-state": ('self.code = code', 'self.code = code\n        self.extra = True'),
        "missing-helper": (repair.RESTORER, ''),
        "duplicate": (repair.REDUCER, repair.REDUCER + repair.REDUCER),
    }
    if mutation == "extra-import":
        text += '\nimport os\n'
    elif mutation == "comment":
        text += '\n# unauthorized bytes\n'
    else:
        old, new = changes[mutation]
        assert text.count(old) == 1
        text = text.replace(old, new, 1)
    path.write_text(text)
    with pytest.raises(AssertionError):
        repair.original_parser_bytes(root)


@pytest.mark.parametrize("parser_repaired", [False, True], ids=["parser-pre", "parser-post"])
@pytest.mark.parametrize("newline", ["whole-crlf", "one-crlf", "whole-cr"])
def test_r06_raw_newline_mutations_are_rejected_on_both_shapes(tmp_path, parser_repaired, newline):
    root = repair.make_shape(tmp_path / "shape", parser_repaired)
    path = root / repair.PARSER
    original = path.read_bytes()
    assert repair.repaired(original) is parser_repaired
    assert b"\r" not in original
    assert repair.original_parser_bytes(root) == repair.original_parser_bytes(repair.ROOT)
    if newline == "whole-crlf":
        changed = original.replace(b"\n", b"\r\n")
    elif newline == "one-crlf":
        changed = original.replace(b"\n", b"\r\n", 1)
    else:
        changed = original.replace(b"\n", b"\r")
    assert changed != original
    assert repair.dump(ast.parse(changed)) == repair.dump(ast.parse(original))
    path.write_bytes(changed)
    # Both the inverse and the real migrated readonly reader must keep raw bytes.
    for reader in (repair.original_parser_bytes,
                   lambda directory: inherited.readonly_bytes(directory, repair.PARSER)):
        with pytest.raises(AssertionError, match="unapproved parser byte change|ambiguous raw repair inverse"):
            reader(root)


def test_r06_changed_original_manifest_is_rejected(tmp_path, monkeypatch):
    copied = tmp_path / "evidence"
    shutil.copytree(repair.FIXTURES, copied)
    (copied / "baseline.json").write_bytes((copied / "baseline.json").read_bytes() + b'\n')
    monkeypatch.setattr(repair, "FIXTURES", copied)
    with pytest.raises(AssertionError, match="baseline changed"):
        repair.baseline()


def test_r06_changed_original_carrier_is_rejected(tmp_path, monkeypatch):
    copied = tmp_path / "evidence"
    shutil.copytree(repair.FIXTURES, copied)
    (copied / "original-carrier-0.txt").write_text("not immutable Git evidence\n")
    monkeypatch.setattr(repair, "FIXTURES", copied)
    with pytest.raises(AssertionError):
        repair.evidence("original-carrier-0.txt")
