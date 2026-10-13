"""P09: real repair guard, actual pre/post copies, and bounded mutations."""

import ast

import pytest

from tests import liss_0587_guard_support as partial
from tests import test_liss_0583_repair_boundary_migration_red as foreach
from tests import test_liss_0584_repair_boundary_red as repair
from tests import test_liss_0585_tensor_guard_migration_red as tensor
from tests import test_liss_0586_host_guard_migration_red as host


@pytest.fixture
def guarded(tmp_path):
    tensor.copy_guarded_dependencies(partial.ROOT, tmp_path)
    path = "compiler/staqex/runtime/evaluation/static_foreach.py"
    (tmp_path / path).write_bytes((partial.ROOT / path).read_bytes())
    return tmp_path


def check(directory, monkeypatch):
    monkeypatch.setattr(repair, "ROOT", directory)
    repair.test_existing_f05_owner_and_readonly_dependencies_are_preserved()


@pytest.mark.parametrize("extracted", [False, True], ids=["pre-partial", "post-partial"])
def test_p09_real_guard_and_existing_copy_fixtures_keep_distinct_shapes(guarded, monkeypatch, extracted):
    partial.make_shape(guarded, extracted)
    partial.assert_shape(guarded, extracted)
    check(guarded, monkeypatch)
    for suite, fixture in ((foreach, foreach.guarded_tree), (tensor, tensor.guarded_tree), (host, host.guarded)):
        monkeypatch.setattr(suite, "ROOT", guarded)
        destination = guarded / suite.__name__.split(".")[-1]
        # Host fixture obtains its source through tensor's ROOT as passed explicitly.
        copied = fixture.__wrapped__(destination, monkeypatch) if suite is not host else fixture.__wrapped__(destination)
        partial.assert_shape(copied, extracted)
        check(copied, monkeypatch)
        if extracted:
            (copied / partial.SUCCESSOR).unlink()
            with pytest.raises(AssertionError, match="missing partial successor"):
                check(copied, monkeypatch)
    historical = guarded / "historical-foreach"
    monkeypatch.setattr(foreach, "ROOT", guarded)
    copied = foreach.guarded_tree.__wrapped__(historical, monkeypatch)
    foreach.baseline_shape(copied)
    partial.make_shape(copied, False)
    partial.assert_shape(copied, False)
    check(copied, monkeypatch)


@pytest.mark.parametrize("path,old,new", [
    (partial.SUCCESSOR, "return PartialValue(fun_name=partial.fun_name, slots=new_slots)", "return partial"),
    (partial.SUCCESSOR, "\n    slots: list[Expr | None]", "\n    slots: list[Expr]"),
    (partial.SUCCESSOR, "@dataclass", "@dataclass(frozen=True)"),
    (partial.SUCCESSOR, partial.MODULE, "compiler.staqex.runtime.evaluation.partial_calls"),
    (partial.SUCCESSOR, "from .errors import KernelError", "from .errors import KernelError as OtherError"),
    (partial.SUCCESSOR, "from .errors import KernelError", "from .errors import KernelError\nfrom ..evaluator import Evaluator"),
    (partial.SUCCESSOR, "def fill_partial(", "def wrong_function("),
    (partial.SUCCESSOR, "from .errors import KernelError", "from .errors import KernelError\nstate = {}"),
    (partial.EVALUATOR, partial.HOOK, "_fill_partial = _fill_partial_successor"),
    (partial.EVALUATOR, partial.HOOK, "_fill_partial = staticmethod(_make_partial_value)"),
    (partial.EVALUATOR, partial.IMPORT, partial.IMPORT + "\n" + partial.IMPORT),
    (partial.EVALUATOR, "return self.static_register_sizes.get(name)", "return 99"),
])
def test_p09_real_guard_rejects_successor_and_wiring_mutations(guarded, monkeypatch, path, old, new):
    partial.make_shape(guarded, True)
    check(guarded, monkeypatch)
    target = guarded / path
    source = target.read_text()
    assert source.count(old) == 1
    target.write_text(source.replace(old, new, 1))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


@pytest.mark.parametrize("mutation", ["missing-successor", "duplicate-class", "duplicate-body", "duplicate-hook", "extra-state"])
def test_p09_rejects_missing_duplicate_and_extra_ownership(guarded, monkeypatch, mutation):
    partial.make_shape(guarded, True)
    check(guarded, monkeypatch)
    if mutation == "missing-successor":
        (guarded / partial.SUCCESSOR).unlink()
    else:
        tree = ast.parse((guarded / partial.EVALUATOR).read_text())
        cls = partial.owner(tree)
        if mutation == "duplicate-class":
            tree.body.append(partial.original_nodes()[0])
        elif mutation == "duplicate-body":
            cls.body.append(partial.original_nodes()[1])
        elif mutation == "duplicate-hook":
            cls.body.append(ast.parse(partial.HOOK).body[0])
        else:
            cls.body.append(ast.parse("state = {}").body[0])
        (guarded / partial.EVALUATOR).write_text(ast.unparse(ast.fix_missing_locations(tree)))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


@pytest.mark.parametrize("extracted", [False, True])
def test_p09_changed_retained_body_and_class_rejected_in_each_shape(guarded, monkeypatch, extracted):
    partial.make_shape(guarded, extracted)
    check(guarded, monkeypatch)
    partial.make_shape(guarded, False)
    path = guarded / partial.EVALUATOR
    original = path.read_text()
    path.write_text(original.replace("return PartialValue(fun_name=partial.fun_name, slots=new_slots)", "return partial"))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)
    path.write_text(original.replace("slots: list[Expr | None]", "slots: list[Expr]"))
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)


def test_p09_original_fixture_hash_and_whole_ast_are_fixed(tmp_path, monkeypatch):
    original = partial.original_nodes()
    assert isinstance(original[0], ast.ClassDef) and isinstance(original[1], ast.FunctionDef)
    fixture = tmp_path / "altered.txt"
    fixture.write_bytes(partial.FIXTURE.read_bytes() + b"\n")
    monkeypatch.setattr(partial, "FIXTURE", fixture)
    with pytest.raises(AssertionError, match="evidence changed"):
        partial.original_nodes()


@pytest.mark.parametrize("path", foreach.BYTE_PATHS)
def test_p09_existing_five_byte_dependencies_still_reject_changes(guarded, monkeypatch, path):
    partial.make_shape(guarded, True)
    check(guarded, monkeypatch)
    target = guarded / path
    target.write_bytes(target.read_bytes() + b"\n# forbidden change\n")
    with pytest.raises(AssertionError):
        check(guarded, monkeypatch)
