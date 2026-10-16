"""O09 strict, distinct AST-only pre/post roots and real inherited guards."""

import ast
import hashlib
import shutil

import pytest

from tests import liss_0590_guard_support as guard
from tests import test_liss_0584_repair_boundary_red as repair
from tests import test_liss_0587_partial_ownership_red as partial
from tests import test_liss_0588_closed_ownership_red as closed
from tests import test_liss_0589_capture_ownership_red as capture


@pytest.fixture(params=[False, True], ids=["pre", "post"])
def shape(request, tmp_path):
    return guard.make_shape(tmp_path / ("post" if request.param else "pre"), request.param)


def test_o09_distinct_roots_reconstruct_original_bytes(tmp_path):
    pre = guard.make_shape(tmp_path / "pre", False)
    post = guard.make_shape(tmp_path / "post", True)
    assert (pre / guard.TYPECHECK).read_bytes() != (post / guard.TYPECHECK).read_bytes()
    assert not guard.installed(ast.parse((pre / guard.TYPECHECK).read_text()))
    assert guard.installed(ast.parse((post / guard.TYPECHECK).read_text()))
    assert guard.readonly_bytes(pre, guard.TYPECHECK) == guard.readonly_bytes(post, guard.TYPECHECK)


def test_o09_real_repair_guard_and_original_mutations(shape, monkeypatch):
    monkeypatch.setattr(repair, "ROOT", shape)
    # Its immutable fixture is deliberately still the real pinned evidence.
    repair.test_typechecker_outside_numeric_inference_is_preserved()
    for mutation in ("unrelated-body", "numeric-signature", "new-state"):
        repair.test_boundary_detects_unapproved_typechecker_changes(mutation)
    repair.test_boundary_allows_only_numeric_body_change_not_signature()


def test_o09_real_readonly_carriers_with_inherited_copy_setup(shape, monkeypatch):
    # Copy each original manifest's actual dependencies, as inherited guard
    # setups do, leaving the new AST-only owner/wiring files distinct.
    manifest_paths = [
        "tests/fixtures/liss_0587/readonly-boundary.json",
        "tests/fixtures/liss_0588/readonly-boundary.json",
        "tests/fixtures/liss_0589/readonly-boundary.json",
    ]
    import json
    for manifest in manifest_paths:
        evidence = json.loads((guard.ROOT / manifest).read_text())
        for path in evidence["readonly_sha256"]:
            if path in {guard.TYPECHECK, guard.CLOSED_CARRIER}:
                continue
            target = shape / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(guard.ROOT / path, target)
    monkeypatch.setattr(partial, "ROOT", shape)
    monkeypatch.setattr(closed.closed, "ROOT", shape)
    monkeypatch.setattr(capture.capture, "ROOT", shape)
    partial.test_p05_p08_consumers_behavior_tests_and_unrelated_owners_are_readonly()
    closed.test_c08_readonly_sources_adjacent_tests_and_prior_fixtures()
    capture.test_s08_all_39_readonly_sources_tests_and_fixtures()


@pytest.mark.parametrize("mutation", ["missing-owner", "missing-context", "literal", "factory", "alias", "duplicate", "extra-import"])
def test_o09_post_projection_rejects_unapproved_wiring(tmp_path, mutation):
    root = guard.make_shape(tmp_path / "post", True)
    path = root / guard.TYPECHECK
    if mutation == "missing-owner":
        (root / guard.OPERATORS).unlink()
    elif mutation == "missing-context":
        (root / guard.CONTEXT).unlink()
    elif mutation == "literal":
        target = root / guard.OPERATORS
        target.write_text(target.read_text().replace("1000000", "1000001"))
    elif mutation == "factory":
        path.write_text(path.read_text().replace('Ty("Meta", "Index", DIMLESS)', 'Ty("Meta", "Wrong", DIMLESS)'))
    elif mutation == "alias":
        path.write_text(path.read_text().replace("_legacy_check_operator = _operator_check_successor", "_legacy_check_operator = check_operator_expr"))
    elif mutation == "duplicate":
        path.write_text(path.read_text().replace(guard.BLOCK, guard.BLOCK + guard.evidence_bytes("original-operator.txt").decode()))
    else:
        target = root / guard.OPERATORS
        target.write_text(target.read_text() + "\nimport os\n")
    with pytest.raises(AssertionError):
        guard.readonly_bytes(root, guard.TYPECHECK)


def test_o09_unrelated_bytes_and_carrier_mutation_not_erased(shape):
    path = shape / guard.TYPECHECK
    path.write_text(path.read_text() + "\n# unapproved byte change\n")
    assert hashlib.sha256(guard.readonly_bytes(shape, guard.TYPECHECK)).hexdigest() != guard.baseline()["typecheck_sha256"]
    carrier = shape / guard.CLOSED_CARRIER
    carrier.write_text(carrier.read_text() + "\n# unapproved carrier edit\n")
    with pytest.raises(AssertionError, match="unapproved closed carrier edit"):
        guard.readonly_bytes(shape, guard.CLOSED_CARRIER)


def test_o09_changed_original_evidence_is_rejected(tmp_path, monkeypatch):
    copied = tmp_path / "evidence"
    shutil.copytree(guard.FIXTURES, copied)
    monkeypatch.setattr(guard, "FIXTURES", copied)
    (copied / "original-operator.txt").write_text("not original\n")
    with pytest.raises(AssertionError):
        guard.original_method()
