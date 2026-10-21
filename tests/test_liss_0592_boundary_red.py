"""R04/R06/R07: actual production repair requirement and frozen outside scope."""

import ast
import importlib
import subprocess
from tests import liss_0591_guard_support as primary

from tests import liss_0592_guard_support as guard


def test_r06_actual_parser_has_exact_reducer_and_restorer():
    data = (guard.ROOT / guard.PARSER).read_bytes()
    assert guard.repaired(data), "ParseError repair not implemented"
    guard.original_parser_bytes(guard.ROOT)


def test_r06_original_parser_and_other_production_are_frozen():
    record = guard.baseline()
    assert record["base"] == "22335a5768c17a41eb94682e7dd14d3e6df004bd"
    assert guard.sha(guard.original_parser_bytes(guard.ROOT)) == record["parser_sha256"]
    for path, expected in record["readonly_sha256"].items():
        assert guard.sha(primary.readonly_bytes(guard.ROOT, path)) == expected, path
    actual = set(subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "compiler"],
        cwd=guard.ROOT, text=True,
    ).splitlines())
    assert primary.production_paths(guard.ROOT, actual) == set(record["production_paths"])


def test_r06_only_two_reviewed_carrier_substitutions_and_old_tests_unchanged():
    guard.assert_carriers()
    paths = subprocess.check_output(["git", "ls-files", "tests"], cwd=guard.ROOT, text=True).splitlines()
    paths = primary.historical_test_paths(paths)
    retained = [p for p in paths if p not in guard.baseline()["carriers"]
                and "/liss_0592/" not in p and "liss_0592_" not in p]
    fingerprint = "\n".join(path + ":" + guard.sha(primary.historical_test_bytes(guard.ROOT, path)) for path in retained)
    assert guard.sha(fingerprint.encode()) == guard.baseline()["protected_tests_fingerprint"]


def test_r04_actual_public_exports_and_class_identity_stay_available():
    from compiler.staqex.parser import ParseError
    from compiler.staqex import pipeline_legacy, modules
    assert ParseError is pipeline_legacy.ParseError is modules.ParseError
    for name, expected in guard.baseline()["exports"].items():
        module = importlib.import_module(name)
        actual = set(module.__all__ if hasattr(module, "__all__") else (n for n in vars(module) if not n.startswith("_")))
        assert actual == set(expected), name
