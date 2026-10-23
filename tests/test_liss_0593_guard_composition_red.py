"""F07–F10: real guard readers on distinct raw roots; no proposed runtime import."""

import ast
import hashlib
import importlib
from pathlib import Path
import shutil
import subprocess
import sys
import types

import pytest

from tests import liss_0593_guard_support as guard


def make_shape(directory, shape):
    sources = ({path: guard.evidence(path) for path in guard.SOURCES}
               if shape == "pre" else guard.expected_sources())
    for path, data in sources.items():
        target = directory / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    assert guard.source_shape(directory) == shape
    return directory


def carrier_module(number, proposed):
    path = guard.CARRIERS[number]
    raw = guard.carrier_after(path) if proposed else (guard.ROOT / path).read_bytes()
    module = types.ModuleType("staged_test_carrier_" + str(number))
    module.__file__ = str(guard.ROOT / path)
    # Only proposed TEST plumbing executes; proposed production stays raw data.
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


@pytest.mark.parametrize("path", guard.SOURCES)
@pytest.mark.parametrize("reader", [0, 1], ids=["0590", "0591"])
def test_f09_actual_unmodified_reader_accepts_future_shape(tmp_path, reader, path):
    root = make_shape(tmp_path / "post", "post")
    actual = importlib.import_module("tests.liss_0590_guard_support" if reader == 0 else "tests.liss_0591_guard_support")
    assert actual.readonly_bytes(root, path) == guard.evidence(path), "carrier integration intentionally pending test acceptance"


@pytest.mark.parametrize("shape", ["pre", "post"])
@pytest.mark.parametrize("reader", [0, 1], ids=["0590", "0591"])
@pytest.mark.parametrize("path", guard.SOURCES)
def test_f07_f09_proposed_real_readers_accept_each_intact_shape(tmp_path, shape, reader, path):
    root = make_shape(tmp_path / shape, shape)
    carrier = carrier_module(reader, True)
    assert carrier.readonly_bytes(root, path) == guard.evidence(path)
    assert guard.source_shape(root) == shape


MUTATIONS = ("missing", "crlf", "mixed-newline", "comment", "body", "order", "wiring", "duplicate", "extra-import")


def mutate(path, mutation):
    raw = path.read_bytes()
    if mutation == "missing":
        path.unlink()
        return
    if mutation == "crlf":
        raw = raw.replace(b"\n", b"\r\n")
    elif mutation == "mixed-newline":
        raw = raw.replace(b"\n", b"\r\n", 1)
    elif mutation == "comment":
        raw += b"\n# unauthorized bytes\n"
    elif mutation == "body":
        assert b"return " in raw
        raw = raw.replace(b"return ", b"raise ", 1)
    elif mutation == "order":
        lines = raw.splitlines(keepends=True)
        lines[0], lines[1] = lines[1], lines[0]
        raw = b"".join(lines)
    elif mutation == "wiring":
        name = b"semantic_fingerprint" if b"semantic_fingerprint" in raw else b"build_inspection"
        raw = raw.replace(name, name + b"_wrong", 1)
    elif mutation == "duplicate":
        raw += raw.splitlines(keepends=True)[0]
    else:
        assert mutation == "extra-import"
        raw += b"\nimport os\n"
    path.write_bytes(raw)


@pytest.mark.parametrize("shape", ["pre", "post"])
@pytest.mark.parametrize("reader", [0, 1], ids=["0590", "0591"])
@pytest.mark.parametrize("path", guard.SOURCES)
@pytest.mark.parametrize("mutation", MUTATIONS)
def test_f07_f09_each_real_reader_rejects_source_mutations(tmp_path, shape, reader, path, mutation):
    root = make_shape(tmp_path / shape, shape)
    carrier = carrier_module(reader, True)
    assert carrier.readonly_bytes(root, path) == guard.evidence(path)
    mutate(root / path, mutation)
    with pytest.raises((AssertionError, OSError)):
        carrier.readonly_bytes(root, path)


@pytest.mark.parametrize("shape", ["pre", "post"])
@pytest.mark.parametrize("reader", [0, 1], ids=["0590", "0591"])
def test_f07_complete_shape_requires_real_siblings_too(tmp_path, shape, reader):
    root = make_shape(tmp_path / shape, shape)
    carrier = carrier_module(reader, True)
    assert carrier.readonly_bytes(root, guard.FINGERPRINT) == guard.evidence(guard.FINGERPRINT)
    (root / guard.BUILDER).unlink()
    with pytest.raises(OSError):
        carrier.readonly_bytes(root, guard.FINGERPRINT)


def test_f09_pre_and_post_are_not_labels_for_the_same_shape(tmp_path):
    pre, post = make_shape(tmp_path / "pre", "pre"), make_shape(tmp_path / "post", "post")
    for path in guard.SOURCES:
        assert (pre / path).read_bytes() != (post / path).read_bytes()
        assert guard.readonly_bytes(pre, path) == guard.readonly_bytes(post, path)
    legacy = ast.parse((post / guard.LEGACY).read_bytes())
    assert not ({n.name for n in legacy.body if isinstance(n, ast.FunctionDef)} & set(guard.FUNCTIONS))
    for name, path in guard.FUNCTIONS.items():
        assert guard.definition((post / path).read_bytes(), name) == guard.definition(guard.evidence(guard.LEGACY), name)


@pytest.mark.parametrize("path", guard.CARRIERS)
@pytest.mark.parametrize("proposed", [False, True], ids=["original", "composed"])
def test_f07_f09_carrier_inverse_retains_only_exact_approved_substitutions(tmp_path, path, proposed):
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    data = guard.carrier_after(path) if proposed else guard.evidence(path)
    target.write_bytes(data)
    assert guard.historical_carrier_bytes(tmp_path, path, data) == guard.evidence(path)
    changed = data + b"\n# unrelated carrier mutation\n"
    target.write_bytes(changed)
    with pytest.raises(AssertionError):
        guard.historical_carrier_bytes(tmp_path, path, changed)
    target.unlink()
    with pytest.raises(OSError):
        guard.historical_carrier_bytes(tmp_path, path, data)


def closure_root(directory):
    for path in (guard.CARRIERS[1], "tests/liss_0593_guard_support.py"):
        target = directory / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(guard.carrier_after(path) if path == guard.CARRIERS[1] else (guard.ROOT / path).read_bytes())
    guard.assert_inverse_closure(directory)
    return directory


def test_f08_exact_pure_closure_preserves_no_production_execution(tmp_path):
    guard.assert_inverse_closure(closure_root(tmp_path))


@pytest.mark.parametrize("path", [guard.CARRIERS[1], "tests/liss_0593_guard_support.py"])
@pytest.mark.parametrize("addition", [
    b"\nfrom compiler.staqex import pipeline\n", b"\nfrom tests import canonical_execution\n",
    b"\nexec('pass')\n", b"\n__import__('compiler.staqex')\n",
    b"\ncompile('pass', 'x', 'exec')\n", b"\nfrom . import other\n",
])
def test_f08_no_transitive_project_import_or_dynamic_execution_escape(tmp_path, path, addition):
    root = closure_root(tmp_path)
    target = root / path
    target.write_bytes(target.read_bytes() + addition)
    with pytest.raises(AssertionError):
        guard.assert_inverse_closure(root)


def full_guard_root(destination, shape):
    """Real local file/Git inventory; never import proposed production files."""
    paths = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "compiler", "tests"],
        cwd=guard.ROOT, text=True,
    ).splitlines()
    for relative in paths:
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(guard.ROOT / relative, target)
    make_shape(destination, shape)
    for path in guard.CARRIERS:
        (destination / path).write_bytes(guard.carrier_after(path))
    subprocess.run(["git", "init", "-q", str(destination)], check=True, capture_output=True)
    subprocess.run(["git", "add", "compiler", "tests"], cwd=destination, check=True, capture_output=True)
    return destination


@pytest.mark.parametrize("shape", ["pre", "post"])
def test_f09_real_frozen_loops_and_0592_test_cohort_on_copied_roots(tmp_path, monkeypatch, shape):
    root = full_guard_root(tmp_path / shape, shape)
    # Initialize real consumer globals before temporary module substitution;
    # selection order must not leak staged modules into later tests.
    old90 = importlib.import_module("tests.test_liss_0590_operator_ownership_red")
    old92 = importlib.import_module("tests.test_liss_0592_boundary_red")
    repair = importlib.import_module("tests.liss_0592_guard_support")
    stage90, stage91, stage_ownership = (carrier_module(i, True) for i in range(3))
    for stage, number in ((stage90, "0590"), (stage91, "0591")):
        stage.ROOT = root
        stage.FIXTURES = root / ("tests/fixtures/liss_" + number)
    tests_package = importlib.import_module("tests")
    for name, stage in (("liss_0590_guard_support", stage90), ("liss_0591_guard_support", stage91)):
        monkeypatch.setitem(sys.modules, "tests." + name, stage)
        monkeypatch.setattr(tests_package, name, stage)
    monkeypatch.setattr(old90, "guard", stage90)
    monkeypatch.setattr(old92, "primary", stage91)
    monkeypatch.setattr(repair, "ROOT", root)
    stage_ownership.guard = stage91
    old90.test_o07_original_facade_bytes_and_other_production_are_preserved()
    stage_ownership.test_p10_unrelated_production_and_all_six_carriers_keep_frozen_bytes()
    stage_ownership.test_b06_pure_inverse_has_no_project_import_or_executable_proposal()
    old92.test_r06_original_parser_and_other_production_are_frozen()
    old92.test_r06_only_two_reviewed_carrier_substitutions_and_old_tests_unchanged()
    # Negative controls exercise the real loops after their intact positives.
    unrelated = root / "compiler/staqex/unitarity_check.py"
    raw = unrelated.read_bytes()
    unrelated.write_bytes(raw + b"\n# forbidden unrelated source\n")
    for check in (old90.test_o07_original_facade_bytes_and_other_production_are_preserved,
                  stage_ownership.test_p10_unrelated_production_and_all_six_carriers_keep_frozen_bytes,
                  old92.test_r06_original_parser_and_other_production_are_frozen):
        with pytest.raises(AssertionError):
            check()
    unrelated.write_bytes(raw)
    old_test = root / "tests/test_liss_0548_scientific_semantic_ir_red.py"
    old_test.write_bytes(old_test.read_bytes() + b"\n# forbidden old-test mutation\n")
    with pytest.raises(AssertionError):
        old92.test_r06_only_two_reviewed_carrier_substitutions_and_old_tests_unchanged()


def test_f06_evidence_is_actual_baseline_git_not_self_generated_hashes():
    for path in (*guard.SOURCES, *guard.CARRIERS):
        original = subprocess.check_output(["git", "show", guard.baseline()["base"] + ":" + path], cwd=guard.ROOT)
        assert original == guard.evidence(path)
    for filename, digest in guard.baseline()["evidence_sha256"].items():
        assert hashlib.sha256((guard.FIXTURES / filename).read_bytes()).hexdigest() == digest


# G01–G09: supplement TEST data only. Live helper/caller repair is Green work.
STALE_PRIMARY_SHA = "ceb6de3592e42f3fa9cca29157d58ee65fe3840f6da9798debf5bf64336fd489"
SEMANTIC_TESTS = {
    "tests/liss_0593_guard_support.py", "tests/test_liss_0593_pure_families_red.py",
    "tests/test_liss_0593_guard_composition_red.py",
}
SEMANTIC_FIXTURES = {"tests/fixtures/liss_0593/" + name for name in (
    "baseline.json", "source-legacy.txt", "source-fingerprint.txt",
    "source-builder.txt", "carrier-0.txt", "carrier-1.txt", "carrier-2.txt")}
SEMANTIC_PATHS = tuple(sorted(SEMANTIC_TESTS | SEMANTIC_FIXTURES))
CONTEXT_MESSAGE = "unapproved carrier change"
DEFAULT_MESSAGE = "unauthorized carrier edit"
CONTEXT_CALL = b"    data = historical_carrier_bytes(directory, path, data, rejection_message='unapproved carrier change')\n"
CONSTANT_IMPORT = b"from tests.liss_0593_guard_support import NEW_TESTS as _semantic_tests, NEW_FIXTURES as _semantic_fixtures\n"
CONSTANT_UNIONS = b"NEW_TESTS = NEW_TESTS | _semantic_tests\nNEW_FIXTURES = NEW_FIXTURES | _semantic_fixtures\n\n\n"
CONTEXT_FUNCTION = b'''def historical_carrier_bytes(directory, path, data, *, rejection_message="unauthorized carrier edit"):
    assert (Path(directory) / path).read_bytes() == data, "requested carrier missing/changed"
    if path in CARRIERS:
        original = evidence(path)
        assert data in (original, carrier_after(path)), rejection_message
        return original
    return data
'''


def g_original_additions():
    source = ast.parse(guard.evidence(guard.CARRIERS[1]))
    node = next(n for n in source.body if isinstance(n, ast.Assign) and any(
        isinstance(t, ast.Name) and t.id == "NEW_TESTS" for t in n.targets))
    tests = ast.literal_eval(node.value)
    fixtures = {"tests/fixtures/liss_0591/" + name for name in (
        "baseline.json", "original-primary.txt", "original-operators.txt",
        *("carrier-%d.txt" % i for i in range(6)), "behavior.json")}
    assert len(tests) == 6 and len(fixtures) == 10
    return tests, fixtures


def g_stale_primary():
    """Reconstruct V1 from immutable bytes, not the current V2 generator."""
    data = guard.evidence(guard.CARRIERS[1])
    dispatch = ("    if path in " + repr(guard.SOURCES) + ":\n"
                "        from tests.liss_0593_guard_support import readonly_bytes as semantic_bytes\n"
                "        return semantic_bytes(directory, path)\n").encode()
    changes = (
        (b"def readonly_bytes(directory, path):\n", b"def readonly_bytes(directory, path):\n" + dispatch),
        (b"    data = (Path(directory) / path).read_bytes()\n",
         b"    data = (Path(directory) / path).read_bytes()\n    from tests.liss_0593_guard_support import historical_carrier_bytes\n    data = historical_carrier_bytes(directory, path, data)\n"),
        (b"    assert actual - old == NEW_TESTS | NEW_FIXTURES,",
         b"    from tests.liss_0593_guard_support import new_test_paths\n    assert actual - old == NEW_TESTS | NEW_FIXTURES | new_test_paths(),"),
        (b"        assert (Path(directory) / path).read_bytes() == carrier_after(path), path",
         b"        from tests.liss_0593_guard_support import historical_carrier_bytes\n        assert historical_carrier_bytes(directory, path, (Path(directory) / path).read_bytes()) == carrier_after(path), path"),
    )
    for original, replacement in changes:
        data = guard.replace_once(data, original, replacement)
    assert guard.sha(data) == STALE_PRIMARY_SHA
    return data


def g_repaired_carriers():
    data = g_stale_primary()
    data = guard.replace_once(data, b"import ast\n", b"import ast\n" + CONSTANT_IMPORT)
    data = guard.replace_once(data, b"def sha(data):\n", CONSTANT_UNIONS + b"def sha(data):\n")
    data = guard.replace_once(data, b"    data = historical_carrier_bytes(directory, path, data)\n", CONTEXT_CALL)
    return {p: data if p == guard.CARRIERS[1] else guard.carrier_after(p) for p in guard.CARRIERS}


def g_proposed_helper(carriers):
    """Pure temporary TEST module; static raw carrier data has no project callback."""
    raw = (guard.ROOT / "tests/liss_0593_guard_support.py").read_bytes()
    generator = ("def carrier_after(path):\n    return " + repr(carriers) + "[path]\n").encode()
    raw = guard.replace_once(raw, guard.definition(raw, "carrier_after"), generator)
    return guard.replace_once(raw, guard.definition(raw, "historical_carrier_bytes"), CONTEXT_FUNCTION)


def g_load(raw, path, root):
    module = types.ModuleType("supplement_" + Path(path).stem)
    module.__file__ = str(root / path)
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def g_stage(root, monkeypatch, shape="post", full=False):
    importlib.import_module("tests.liss_0591_guard_support")
    if full:
        full_guard_root(root, shape)
    else:
        paths = {*guard.NEW_TESTS, *guard.NEW_FIXTURES}
        paths.update(str(p.relative_to(guard.ROOT)) for p in (guard.ROOT / "tests/fixtures/liss_0591").iterdir() if p.is_file())
        for path in paths:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(guard.ROOT / path, target)
        make_shape(root, shape)
    carriers = g_repaired_carriers()
    helper_path = "tests/liss_0593_guard_support.py"
    helper_raw = g_proposed_helper(carriers)
    (root / helper_path).write_bytes(helper_raw)
    for path, raw in carriers.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    helper = g_load(helper_raw, helper_path, root)
    package = importlib.import_module("tests")
    monkeypatch.setitem(sys.modules, "tests.liss_0593_guard_support", helper)
    monkeypatch.setattr(package, "liss_0593_guard_support", helper)
    primary = g_load(carriers[guard.CARRIERS[1]], guard.CARRIERS[1], root)
    monkeypatch.setitem(sys.modules, "tests.liss_0591_guard_support", primary)
    monkeypatch.setattr(package, "liss_0591_guard_support", primary)
    return helper, primary


def g_listing(primary, monkeypatch):
    tests, fixtures = g_original_additions()
    old = set(primary.baseline()["test_paths"])
    actual = old | tests | fixtures | set(SEMANTIC_PATHS)
    monkeypatch.setattr(primary.subprocess, "check_output", lambda *args, **kwargs: "\n".join(sorted(actual)) + "\n")
    assert set(primary.historical_test_paths(sorted(actual))) == old
    return old, actual


def g_inventory_contract(helper, primary, monkeypatch, mode, path=None):
    old, actual = g_listing(primary, monkeypatch)
    if mode == "listing-missing":
        actual.remove(path)
    elif mode == "artifact-missing":
        (helper.ROOT / path).unlink()
    elif mode == "extra":
        actual.add("tests/unexpected.py")
    else:
        assert mode == "original-missing"
        actual.remove(sorted(old)[0])
    rejected = False
    try:
        primary.historical_test_paths(sorted(actual))
    except AssertionError:
        rejected = True
    assert rejected, "inventory negative control was accepted"


def g_diagnostic_contract(primary, target):
    path = guard.CARRIERS[0]
    target = target / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(primary.carrier_after(path))
    assert primary.historical_test_bytes(target.parents[1], path) == primary.evidence(primary.baseline()["carriers"][path])
    target.write_bytes(target.read_bytes() + b"\n# unapproved carrier bytes\n")
    with pytest.raises(AssertionError) as caught:
        primary.historical_test_bytes(target.parents[1], path)
    assert caught.value.args == (CONTEXT_MESSAGE,)


def g_stale_contract(helper, root):
    path = guard.CARRIERS[1]
    target = root / path
    assert helper.historical_carrier_bytes(root, path, target.read_bytes()) == guard.evidence(path)
    stale = helper.carrier_after(path)
    stale = guard.replace_once(stale, CONSTANT_IMPORT, b"")
    stale = guard.replace_once(stale, CONSTANT_UNIONS, b"")
    stale = guard.replace_once(stale, CONTEXT_CALL, b"    data = historical_carrier_bytes(directory, path, data)\n")
    assert stale == g_stale_primary() and guard.sha(stale) == STALE_PRIMARY_SHA
    target.write_bytes(stale)
    rejected = False
    try:
        helper.historical_carrier_bytes(root, path, stale)
    except AssertionError:
        rejected = True
    assert rejected, "stale-post negative control was accepted"


def test_g01_g06_production_and_original_consumer_contracts_remain_fixed():
    expected = {
        guard.LEGACY: "aba64717dfcf9026d446fea40c62fe3f95fb53beb0b7f277c94fd3f783d16c33",
        guard.FINGERPRINT: "c236a961f4a0dc5c9a680f74d9c0e46e8f60f40f5005bb3ee51286818201fdd6",
        guard.BUILDER: "fb74b724a9cdd9cc6cac0748b863d7f7b09d551f06a410dfaa2b5e425ae90bee",
        guard.CARRIERS[0]: "82792053141d17f57b1d22f176ca814122bfc747adc7aa54120cf2ef5c1dc65c",
        guard.CARRIERS[2]: "04d967380221caad8b83894ec5c05cd53317ce7339036129a1952f3bfc559eec",
        "tests/test_liss_0593_pure_families_red.py": "14ccf2da21b738f48552965e4743394425b834416fa7583b875835fe42fd455a",
    }
    for path, digest in expected.items():
        assert guard.sha((guard.ROOT / path).read_bytes()) == digest, path
    old_test = "tests/test_liss_0591_guard_migration_red.py"
    assert (guard.ROOT / old_test).read_bytes() == subprocess.check_output(["git", "show", guard.baseline()["base"] + ":" + old_test], cwd=guard.ROOT)
    prefix = b"".join(Path(__file__).read_bytes().splitlines(keepends=True)[:231])
    assert guard.sha(prefix) == "10094175a0438376a5ad1376aca88a60691fa0d4333e867e9ed9f48b32dc12eb"


def test_g02_live_keyword_only_diagnostic_api():
    import inspect
    parameter = inspect.signature(guard.historical_carrier_bytes).parameters.get("rejection_message")
    assert parameter is not None, "keyword-only diagnostic contract not installed"
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY and parameter.default == DEFAULT_MESSAGE


@pytest.mark.parametrize("kind", ["tests", "fixtures"])
def test_g03_live_public_inventory_matches_exact_composed_contract(kind):
    primary = importlib.import_module("tests.liss_0591_guard_support")
    tests, fixtures = g_original_additions()
    expected = tests | SEMANTIC_TESTS if kind == "tests" else fixtures | SEMANTIC_FIXTURES
    assert getattr(primary, "NEW_TESTS" if kind == "tests" else "NEW_FIXTURES") == expected


def test_g03_live_semantic_additions_are_not_mutated_by_composition():
    importlib.import_module("tests.liss_0591_guard_support")
    assert guard.NEW_TESTS == SEMANTIC_TESTS and guard.NEW_FIXTURES == SEMANTIC_FIXTURES


def test_g05_live_generator_and_installed_caller_match_exact_repaired_bytes():
    expected = g_repaired_carriers()[guard.CARRIERS[1]]
    assert guard.carrier_after(guard.CARRIERS[1]) == expected, "corrected-post carrier not installed"
    assert (guard.ROOT / guard.CARRIERS[1]).read_bytes() == expected


def test_g05_live_inverse_does_not_accept_the_failing_stale_post(tmp_path):
    path = guard.CARRIERS[1]
    target = tmp_path / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(guard.evidence(path))
    assert guard.historical_carrier_bytes(tmp_path, path, target.read_bytes()) == guard.evidence(path)
    stale = g_stale_primary()
    target.write_bytes(stale)
    with pytest.raises(AssertionError):
        guard.historical_carrier_bytes(tmp_path, path, stale)


@pytest.mark.parametrize("path", guard.CARRIERS)
@pytest.mark.parametrize("shape", ["original", "corrected"])
@pytest.mark.parametrize("context", [False, True], ids=["default", "caller-context"])
def test_g02_staged_default_and_context_keep_intact_bytes_and_exact_rejection(tmp_path, monkeypatch, path, shape, context):
    helper, _ = g_stage(tmp_path / "stage", monkeypatch)
    target = helper.ROOT / path
    data = guard.evidence(path) if shape == "original" else helper.carrier_after(path)
    target.write_bytes(data)
    kwargs = {"rejection_message": CONTEXT_MESSAGE} if context else {}
    assert helper.historical_carrier_bytes(helper.ROOT, path, data, **kwargs) == guard.evidence(path)
    changed = data + b"\n# unapproved extra bytes\n"
    target.write_bytes(changed)
    with pytest.raises(AssertionError) as caught:
        helper.historical_carrier_bytes(helper.ROOT, path, changed, **kwargs)
    assert caught.value.args == (CONTEXT_MESSAGE if context else DEFAULT_MESSAGE,)


@pytest.mark.parametrize("path", guard.CARRIERS)
def test_g02_staged_context_does_not_swallow_missing_or_evidence_failures(tmp_path, monkeypatch, path):
    helper, _ = g_stage(tmp_path / "stage", monkeypatch)
    target = helper.ROOT / path
    data = target.read_bytes()
    assert helper.historical_carrier_bytes(helper.ROOT, path, data, rejection_message=CONTEXT_MESSAGE) == guard.evidence(path)
    target.unlink()
    with pytest.raises(OSError):
        helper.historical_carrier_bytes(helper.ROOT, path, data, rejection_message=CONTEXT_MESSAGE)
    target.write_bytes(data)
    manifest = helper.FIXTURES / "baseline.json"
    manifest.write_bytes(manifest.read_bytes() + b"\n")
    with pytest.raises(AssertionError) as caught:
        helper.historical_carrier_bytes(helper.ROOT, path, data, rejection_message=CONTEXT_MESSAGE)
    assert caught.value.args == ("0593 evidence changed",)


@pytest.mark.parametrize("path", SEMANTIC_PATHS)
@pytest.mark.parametrize("mode", ["listing-missing", "artifact-missing"])
def test_g04_staged_each_semantic_path_requires_listing_and_real_artifact(tmp_path, monkeypatch, path, mode):
    helper, primary = g_stage(tmp_path / "stage", monkeypatch)
    g_inventory_contract(helper, primary, monkeypatch, mode, path)


@pytest.mark.parametrize("mode", ["extra", "original-missing"])
def test_g04_staged_retains_original_extra_and_missing_rejections(tmp_path, monkeypatch, mode):
    helper, primary = g_stage(tmp_path / "stage", monkeypatch)
    g_inventory_contract(helper, primary, monkeypatch, mode)


@pytest.mark.parametrize("path", guard.CARRIERS)
@pytest.mark.parametrize("shape", ["original", "corrected"])
@pytest.mark.parametrize("mutation", ["comment", "crlf", "mixed-newline", "body", "extra-import"])
def test_g05_staged_carrier_raw_mutations_are_not_normalized(tmp_path, monkeypatch, path, shape, mutation):
    helper, _ = g_stage(tmp_path / "stage", monkeypatch)
    target = helper.ROOT / path
    raw = guard.evidence(path) if shape == "original" else helper.carrier_after(path)
    target.write_bytes(raw)
    assert helper.historical_carrier_bytes(helper.ROOT, path, raw) == guard.evidence(path)
    mutate(target, mutation)
    with pytest.raises(AssertionError):
        helper.historical_carrier_bytes(helper.ROOT, path, target.read_bytes())


def test_g05_staged_stale_post_is_independently_reconstructed_and_rejected(tmp_path, monkeypatch):
    helper, primary = g_stage(tmp_path / "stage", monkeypatch)
    g_stale_contract(helper, helper.ROOT)
    with pytest.raises(AssertionError):
        primary.historical_test_bytes(helper.ROOT, guard.CARRIERS[1])


@pytest.mark.parametrize("first", ["liss_0591_guard_support", "liss_0593_guard_support"])
def test_g03_g07_staged_declared_inventory_is_pure_and_import_order_independent(tmp_path, monkeypatch, first):
    helper, primary = g_stage(tmp_path / "stage", monkeypatch)
    tests, fixtures = g_original_additions()
    assert primary.NEW_TESTS == tests | helper.NEW_TESTS and primary.NEW_FIXTURES == fixtures | helper.NEW_FIXTURES
    assert len(primary.NEW_TESTS | primary.NEW_FIXTURES) == 26
    assert helper.NEW_TESTS == SEMANTIC_TESTS and helper.NEW_FIXTURES == SEMANTIC_FIXTURES
    helper.assert_inverse_closure(helper.ROOT)
    command = [sys.executable, "-c", "import sys,tests,importlib; tests.__path__=[" + repr(str(helper.ROOT / "tests")) + "]; importlib.import_module('tests." + first + "'); p=importlib.import_module('tests.liss_0591_guard_support'); s=importlib.import_module('tests.liss_0593_guard_support'); assert s.NEW_TESTS <= p.NEW_TESTS and s.NEW_FIXTURES <= p.NEW_FIXTURES"]
    result = subprocess.run(command, cwd=guard.ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("fault", ["permissive-inventory", "ignored-artifact-delete", "wrong-diagnostic", "stale-accepted"])
def test_g08_contracts_reject_boundary_specific_counterexamples(tmp_path, fault):
    def contract(helper, primary, patch, root):
        if fault in {"permissive-inventory", "ignored-artifact-delete"}:
            mode = "extra" if fault == "permissive-inventory" else "artifact-missing"
            g_inventory_contract(helper, primary, patch, mode, SEMANTIC_PATHS[0])
        elif fault == "wrong-diagnostic":
            g_diagnostic_contract(primary, root / "exercise")
        else:
            g_stale_contract(helper, helper.ROOT)

    with pytest.MonkeyPatch.context() as patch:
        helper, primary = g_stage(tmp_path / "intact", patch)
        contract(helper, primary, patch, tmp_path / "intact")
    with pytest.MonkeyPatch.context() as patch:
        helper, primary = g_stage(tmp_path / "counterexample", patch)
        calls = []
        g_inject_fault(helper, primary, patch, fault, calls)
        with pytest.raises(AssertionError):
            contract(helper, primary, patch, tmp_path / "counterexample")
        assert len(calls) == 2, "must reach intact positive and mutated negative,not fail in setup"


def g_inject_fault(helper, primary, patch, fault, calls):
    if fault == "permissive-inventory":
        def permissive(paths):
            calls.append("inventory")
            return [p for p in paths if p in primary.baseline()["test_paths"]]
        patch.setattr(primary, "historical_test_paths", permissive)
    elif fault == "ignored-artifact-delete":
        def unchecked():
            calls.append("existence")
            return helper.NEW_TESTS | helper.NEW_FIXTURES
        patch.setattr(helper, "new_test_paths", unchecked)
    else:
        original = helper.historical_carrier_bytes
        def broken(directory, path, data, **kwargs):
            calls.append(fault)
            if fault == "stale-accepted" and guard.sha(data) == STALE_PRIMARY_SHA:
                return guard.evidence(path)
            try:
                return original(directory, path, data, **kwargs)
            except AssertionError:
                assert fault == "wrong-diagnostic"
                raise AssertionError("wrong-diagnostic")
        patch.setattr(helper, "historical_carrier_bytes", broken)


@pytest.mark.parametrize("shape", ["pre", "post"])
def test_g07_original_consumers_and_negative_controls_on_repaired_copied_roots(tmp_path, monkeypatch, shape):
    old90 = importlib.import_module("tests.test_liss_0590_operator_ownership_red")
    old91 = importlib.import_module("tests.test_liss_0591_guard_migration_red")
    old92 = importlib.import_module("tests.test_liss_0592_boundary_red")
    repair = importlib.import_module("tests.liss_0592_guard_support")
    helper, primary = g_stage(tmp_path / shape, monkeypatch, shape, full=True)
    root = helper.ROOT
    stage90 = g_load(helper.carrier_after(guard.CARRIERS[0]), guard.CARRIERS[0], root)
    ownership = g_load(helper.carrier_after(guard.CARRIERS[2]), guard.CARRIERS[2], root)
    monkeypatch.setattr(old90, "guard", stage90)
    monkeypatch.setattr(old91, "guard", primary)
    monkeypatch.setattr(old92, "primary", primary)
    monkeypatch.setattr(repair, "ROOT", root)
    checks = (old90.test_o07_original_facade_bytes_and_other_production_are_preserved,
              ownership.test_p10_unrelated_production_and_all_six_carriers_keep_frozen_bytes,
              old92.test_r06_original_parser_and_other_production_are_frozen)
    for check in checks:
        check()
    ownership.test_b06_pure_inverse_has_no_project_import_or_executable_proposal()
    old92.test_r06_only_two_reviewed_carrier_substitutions_and_old_tests_unchanged()
    for path in primary.baseline()["carriers"]:
        old91.test_b04_b05_each_of_six_carriers_rejects_extra_edits(tmp_path / "old-cases", path)
    with pytest.MonkeyPatch.context() as context:
        old91.test_b08_closed_new_test_inventory_rejects_extra_or_missing_paths(context)
    g_original_consumer_mutations(root, checks, old92, primary)


def g_original_consumer_mutations(root, checks, old92, primary):
    unrelated = root / "compiler/staqex/unitarity_check.py"
    original = unrelated.read_bytes()
    unrelated.write_bytes(original + b"\n# forbidden unrelated source\n")
    for check in checks:
        with pytest.raises(AssertionError):
            check()
    unrelated.write_bytes(original)
    parser = root / primary.PARSER
    original = parser.read_bytes()
    assert primary.readonly_bytes(root, primary.PARSER)
    parser.write_bytes(original + b"\ninvalid (\n")
    with pytest.raises(SyntaxError):
        primary.readonly_bytes(root, primary.PARSER)
    parser.write_bytes(original)
    old_test = root / "tests/test_liss_0548_scientific_semantic_ir_red.py"
    old_test.write_bytes(old_test.read_bytes() + b"\n# forbidden old-test mutation\n")
    with pytest.raises(AssertionError):
        old92.test_r06_only_two_reviewed_carrier_substitutions_and_old_tests_unchanged()
