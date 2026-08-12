"""AT-TDD: LISS-0327 HostInputPort foundation (ADR 0194 Follow-up item 1)."""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path
from typing import Any, Iterator

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import host as host_module  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.host_input_binding import (  # noqa: E402
    HOST_INPUT_BINDING_MISSING,
    HOST_INPUT_BINDING_VALUE_ERROR,
    validate_matrix_binding,
)
from compiler.staqex.host_input_port import MappingHostInputAdapter  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_injected_host_input_is_readable_by_name() -> None:
    port = MappingHostInputAdapter({"m": [[True, False], [False, True]]})
    evaluator = Evaluator(seed=0, host_input=port)

    assert evaluator.host_input is port
    assert evaluator.host_input.get("m") == [[True, False], [False, True]]


def test_no_host_input_injected_defaults_to_none() -> None:
    evaluator = Evaluator(seed=0)

    assert evaluator.host_input is None


def test_valid_symmetric_bool_matrix_passes_validation() -> None:
    matrix = [
        [True, True, False],
        [True, True, True],
        [False, True, True],
    ]
    diagnostics = validate_matrix_binding("m", matrix, 3, dtype=bool)

    assert diagnostics == []


def test_missing_binding_fails_closed() -> None:
    diagnostics = validate_matrix_binding("m", None, 3, dtype=bool)

    codes = {d["code"] for d in diagnostics}
    assert HOST_INPUT_BINDING_MISSING in codes


def test_non_square_matrix_fails_closed() -> None:
    diagnostics = validate_matrix_binding(
        "m", [[True, False], [False, True], [True, True]], 3, dtype=bool
    )

    codes = {d["code"] for d in diagnostics}
    assert HOST_INPUT_BINDING_VALUE_ERROR in codes


def test_asymmetric_matrix_fails_closed() -> None:
    matrix = [
        [True, True, False],
        [False, True, True],
        [False, True, True],
    ]
    diagnostics = validate_matrix_binding("m", matrix, 3, dtype=bool)

    codes = {d["code"] for d in diagnostics}
    assert HOST_INPUT_BINDING_VALUE_ERROR in codes


@contextlib.contextmanager
def _patched_evaluator(replacement: Any) -> Iterator[None]:
    """Dependency-free stand-in for pytest's ``monkeypatch.setattr``, matching
    the established idiom in
    ``tests/test_simulator_resource_execution_wiring_red.py`` (no pytest
    configuration; suites run as plain scripts, LISS-0208)."""

    original = host_module.Evaluator
    host_module.Evaluator = replacement
    try:
        yield
    finally:
        host_module.Evaluator = original


def test_settings_inputs_passes_through_to_evaluator_construction() -> None:
    captured: dict[str, Any] = {}

    class _CapturingEvaluator(Evaluator):
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)
            super().__init__(**kwargs)

    src = """
package t
pub fn main() -> Unit {
    State x = Coin()
    Measure x
}
"""
    with _patched_evaluator(_CapturingEvaluator):
        result = run_source(
            src, settings={"target": "local", "seed": 0, "inputs": {"m": [[True]]}}
        )

    assert result.status == "succeeded", result.diagnostics
    assert "host_input" in captured
    assert captured["host_input"] is not None
    assert captured["host_input"].get("m") == [[True]]
