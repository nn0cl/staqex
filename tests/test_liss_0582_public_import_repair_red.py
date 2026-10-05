"""R01–R05 compatibility contracts; R06–R07 remain delivery gates.

The frozen contract is never regenerated here. Only capture output is written
to pytest temporary storage, using the real script in a fresh interpreter.
"""

from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EVALUATOR = "compiler.staqex.runtime.evaluator"
FROZEN = ROOT / "docs/testing/refactor-baseline.json"
RESTORED_NAMES = (
    "EvolveExpr", "Measure", "OpAttr", "OpBin", "OpBinder", "OpCall",
    "OpIndexed", "OpPauli", "OpPow", "replace",
)
MODULES = (
    EVALUATOR, "compiler.staqex.typecheck", "compiler.staqex.parser",
    "compiler.staqex.scientific_semantic_ir", "compiler.staqex.backend.qasm.lower",
    "compiler.staqex.pipeline",
)
CASE_IDS = (
    "runtime:b01-fixed-seed", "qasm:a08-entangled-ancilla",
    "diagnostic:missing-expression",
)


@pytest.mark.parametrize("name", RESTORED_NAMES)
def test_direct_import_preserves_original_identity(name: str) -> None:
    """R01: import resolution itself must succeed, not an expected exception."""
    namespace: dict[str, object] = {}
    exec(f"from {EVALUATOR} import {name}", namespace)
    owner = importlib.import_module(
        "dataclasses" if name == "replace" else "compiler.staqex.ast_nodes"
    )
    assert namespace[name] is getattr(owner, name)


def test_wildcard_preserves_exact_manifest_and_identity() -> None:
    """R02: compare Python's actual wildcard behavior with the frozen surface."""
    namespace: dict[str, object] = {}
    exec(f"from {EVALUATOR} import *", namespace)
    expected = json.loads(FROZEN.read_text())["public_modules"][EVALUATOR]
    exported = sorted(name for name in namespace if name != "__builtins__")
    assert exported == expected
    evaluator = importlib.import_module(EVALUATOR)
    assert not hasattr(evaluator, "__all__"), "no new restrictive export list"
    for name in expected:
        assert namespace[name] is getattr(evaluator, name)
    for name in RESTORED_NAMES:
        owner = importlib.import_module(
            "dataclasses" if name == "replace" else "compiler.staqex.ast_nodes"
        )
        assert namespace[name] is getattr(owner, name)


@pytest.fixture(scope="module")
def captured_baseline(tmp_path_factory: pytest.TempPathFactory) -> bytes:
    output = tmp_path_factory.mktemp("liss0582-capture") / "actual.json"
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/capture-refactor-baseline.py"),
         "--root", str(ROOT), "--cases",
         str(ROOT / "tests/fixtures/liss_0543/baseline-cases.toml"),
         "--output", str(output)],
        cwd=ROOT, capture_output=True, text=True, check=False, timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return output.read_bytes()


def test_capture_equals_frozen_baseline_bytes(captured_baseline: bytes) -> None:
    """R03: unlike generator determinism, detect drift from the original contract."""
    assert captured_baseline == FROZEN.read_bytes()


@pytest.mark.parametrize("module", MODULES)
def test_capture_preserves_each_public_manifest(
    captured_baseline: bytes, module: str,
) -> None:
    actual = json.loads(captured_baseline)["public_modules"]
    expected = json.loads(FROZEN.read_bytes())["public_modules"]
    assert set(actual) == set(MODULES) == set(expected)
    assert actual[module] == expected[module]


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_capture_preserves_complete_case_payload_and_hash(
    captured_baseline: bytes, case_id: str,
) -> None:
    actual = json.loads(captured_baseline)["cases"]
    expected = json.loads(FROZEN.read_bytes())["cases"]
    assert set(actual) == set(CASE_IDS) == set(expected)
    assert actual[case_id] == expected[case_id]


@pytest.mark.parametrize("consumer,symbols", (
    ("compiler.staqex.cli", ("Evaluator",)),
    ("compiler.staqex.host", ("Evaluator", "EvalResult", "KernelError", "KernelDiagnosticError")),
    ("compiler.staqex.run", ("Evaluator", "EvalResult")),
    ("compiler.staqex.runtime", ("Evaluator", "EvalResult", "MeasureResult")),
    ("compiler.staqex.scientific_semantic.legacy", ()),
))
def test_actual_consumer_imports_in_fresh_process(
    consumer: str, symbols: tuple[str, ...],
) -> None:
    """R04: consumer-first imports also exercise cold import-cycle boundaries."""
    code = (
        "import importlib\n"
        f"consumer = importlib.import_module({consumer!r})\n"
        f"evaluator = importlib.import_module({EVALUATOR!r})\n"
        f"for name in {symbols!r}:\n"
        "    assert getattr(consumer, name) is getattr(evaluator, name)\n"
        "for name in ('Evaluator', 'EvalResult', 'MeasureResult', 'KernelError', "
        "'KernelDiagnosticError', 'ClassInstance', 'EnumValue', '_apply_op'):\n"
        "    assert callable(getattr(evaluator, name))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=ROOT,
        capture_output=True, text=True, check=False, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_legacy_rejection_keeps_evaluator_error_identity() -> None:
    legacy = importlib.import_module("compiler.staqex.scientific_semantic.legacy")
    evaluator = importlib.import_module(EVALUATOR)
    semantic_ir = legacy.ScientificSemanticIR(
        schema="scientific_semantic_ir.v1", authority="not-canonical",
        nodes=(), relations=(),
    )
    # Resolve both entrypoints before asserting the expected semantic rejection.
    build_plan = legacy.build_runtime_execution_plan
    error_type = evaluator.KernelDiagnosticError
    with pytest.raises(error_type, match="canonical semantic authority"):
        build_plan(semantic_ir)


def test_private_rational_consumer_remains_usable() -> None:
    consumer = importlib.import_module("tests.test_classical_rational_red")
    evaluator = importlib.import_module(EVALUATOR)
    assert consumer._apply_op is evaluator._apply_op
    consumer.test_int_div_is_fraction()
    consumer.test_float_div_stays_float()


def test_only_original_facade_imports_are_restored() -> None:
    """R05: freeze old imports while requiring the approved original routes."""
    tree = ast.parse((ROOT / "compiler/staqex/runtime/evaluator.py").read_text())
    retained: list[ast.stmt] = []
    restored: list[str] = []
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        if isinstance(node, ast.ImportFrom):
            kept = []
            for alias in node.names:
                if alias.name not in RESTORED_NAMES:
                    kept.append(alias)
                    continue
                expected_route = ("dataclasses", 0) if alias.name == "replace" else ("ast_nodes", 2)
                assert (node.module, node.level) == expected_route
                assert alias.asname is None
                restored.append(alias.name)
            node.names = kept
            if not kept:
                continue
        retained.append(node)
    assert sorted(restored) == sorted(RESTORED_NAMES)
    tree.body = retained
    digest = hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()
    assert digest == "1fbcee4ff01ad715a09074c5d1f3232e083e89cd23f212df6e5147cb33b6d959"


def test_evaluator_executable_ast_is_unchanged() -> None:
    """R05: only top-level imports/comments may change against repair base."""
    tree = ast.parse((ROOT / "compiler/staqex/runtime/evaluator.py").read_text())
    tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
    digest = hashlib.sha256(ast.dump(tree, include_attributes=False).encode()).hexdigest()
    assert digest == "a745686bf2fb7930b56e950aa2bbc3bc485db08cca494bdb2351a0ca80a2a25d"


@pytest.mark.parametrize("path,digest", (
    ("compiler/staqex/runtime/evaluation/plan_eligibility.py", "b80dc37a8ec7e7b4cd3fa1dc3571e6fc88a3165984c392a270e8068e43f1ec68"),
    ("compiler/staqex/runtime/evaluation/orchestration.py", "beb2fea6c8a21017c552945ea7cafd538912f8c9946951eafc64b9cc71ad029a"),
    ("compiler/staqex/runtime/evaluation/compatibility.py", "f3792eb9c7c8636e1395e74a9faf0d539a7b170549a22ad70a1dc2a944cc2c4a"),
    ("tests/test_liss_0582_runtime_plan_eligibility_red.py", "a9be2ddbe1984414c1e5c0244e15735ba2aa6481036e4c7cc07a2b2482058953"),
    ("docs/testing/refactor-baseline.json", "1dcc3848030fdf48f3c44ebbe8951853b1698cce2ffd75c713d213e22dc99692"),
    ("scripts/capture-refactor-baseline.py", "dbb97e527bb885ef45f140c65067f75d8ee31639f3ef4410156ed6c151a80d5a"),
    ("tests/fixtures/liss_0543/baseline-cases.toml", "e5801237424de6fb10c1a49880e5a71f1d462e42421e79cd4325df4169b18db2"),
))
def test_accepted_ownership_and_baseline_files_are_unchanged(path: str, digest: str) -> None:
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
