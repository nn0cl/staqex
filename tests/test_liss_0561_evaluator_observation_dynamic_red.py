"""Phase 1 Red contracts for LISS-0561 observation and dynamic lanes."""

from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

from compiler.staqex.runtime.evaluator import Evaluator


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR = ROOT / "compiler/staqex/runtime/evaluator.py"
OBSERVATION_IMPORT = "compiler.staqex.runtime.evaluation.observation"
DYNAMIC_IMPORT = "compiler.staqex.runtime.evaluation.dynamic_lane"

OBSERVATION_METHODS = {
    "_execute_deferred_state_measure_plan", "_prepare_first_family_context",
    "_main_deferred_eligible", "_is_deferred_state_bind", "_expr_has_inspect",
    "_expr_free_vars", "_deferred_bind_cone", "_apply_measure_tracing_out",
    "_run_deferred_state_binds", "_mixed_state_for_measure",
    "_resolve_measurement_kind", "_bind_povm", "_bind_mixed_state",
    "_resolve_lindblad_jumps", "_resolve_lindblad_hamiltonian",
    "_compile_lindblad_operator", "_emit_measure_text", "_emit_sink",
    "_measure_mixed", "_expr_marginal", "_measure",
}
DYNAMIC_METHODS = {
    "_run_dynamic_qpu_block", "_reset_dynamic_wire", "_run_dynamic_arm_body",
    "_resolve_dynamic_outcome", "_collapse_dynamic_wire",
}


def _evaluator_method_names() -> set[str]:
    tree = ast.parse(EVALUATOR.read_text(encoding="utf-8"))
    evaluator = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Evaluator"
    )
    return {
        node.name for node in evaluator.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_observation_and_dynamic_lanes_have_internal_modules() -> None:
    for module_name in (OBSERVATION_IMPORT, DYNAMIC_IMPORT):
        module = importlib.import_module(module_name)
        assert "runtime.evaluator" not in inspect.getsource(module)


def test_observation_and_dynamic_method_manifests_leave_evaluator() -> None:
    remaining = _evaluator_method_names() & (OBSERVATION_METHODS | DYNAMIC_METHODS)
    assert not remaining, (
        "observation/dynamic methods remain on Evaluator: "
        f"{sorted(remaining)}"
    )


def test_extracted_lanes_receive_context_instead_of_copying_runtime_state() -> None:
    for module_name in (OBSERVATION_IMPORT, DYNAMIC_IMPORT):
        source = inspect.getsource(importlib.import_module(module_name))
        assert "Evaluator(" not in source
        assert "self.mixed_states" not in source
        assert "self.povms" not in source
        assert "self.host_input" not in source


def test_public_evaluator_import_manifest_remains_available() -> None:
    module = importlib.import_module("compiler.staqex.runtime.evaluator")
    for symbol in (
        "Evaluator", "EvalResult", "MeasureResult", "CanonicalExecutionEvidence"
    ):
        assert hasattr(module, symbol), (
            f"public compatibility symbol missing: {symbol}"
        )


def test_private_consumer_manifest_is_explicit_before_extraction() -> None:
    consumers = {
        "tests/test_deferred_pushforward_mvp_red.py": "_deferred_bind_cone",
        "compiler/staqex/runtime/evaluator.py": "_main_deferred_eligible",
    }
    for relative_path, symbol in consumers.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert symbol in text
