"""AT-TDD Phase 1 Red tests for LISS-0064.

These tests define the missing execution wiring around the provider-neutral
LISS-0063 decision boundary.  They intentionally use the existing run and
QASM entry points with an explicit immutable profile and estimate; no manifest
file, provider SDK, or real QPU is involved.
"""

from __future__ import annotations

import contextlib
import importlib
import io
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _resolve_owner(target: str) -> tuple[Any, str]:
    """Split ``a.b.C.attr`` into the object owning ``attr`` and the name."""
    parts = target.split(".")
    for split in range(len(parts) - 1, 0, -1):
        try:
            owner: Any = importlib.import_module(".".join(parts[:split]))
        except ImportError:
            continue
        for step in parts[split:-1]:
            owner = getattr(owner, step)
        return owner, parts[-1]
    raise ImportError(f"cannot resolve {target!r}")


@contextlib.contextmanager
def _patched(target: str, replacement: Any) -> Iterator[None]:
    """Dependency-free stand-in for pytest's ``monkeypatch.setattr``.

    ``testing-strategy.md`` states the repository has no pytest configuration,
    so suites run as plain scripts (LISS-0208).
    """
    owner, attr = _resolve_owner(target)
    original = getattr(owner, attr)
    setattr(owner, attr, replacement)
    try:
        yield
    finally:
        setattr(owner, attr, original)

from compiler.staqex.codegen_qasm import OpenQASM3Generator  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.resource_profile import (  # noqa: E402
    ResourceProfile,
    SimulationResourceEstimate,
    SimulatorResourceBudget,
)
from compiler.staqex.run import run_source  # noqa: E402


_SOURCE = """
package t
pub fn main() -> Unit {
    State q = |0>
    Measure q
}
"""


def _profile(policy: str) -> ResourceProfile:
    return ResourceProfile(
        simulator=SimulatorResourceBudget(policy=policy, memory_limit_bytes=100)
    )


def _over_limit_estimate() -> SimulationResourceEstimate:
    return SimulationResourceEstimate(
        representation="StateVector",
        logical_qubits=3,
        estimated_bytes=101,
        workspace_factor=3,
    )


def test_local_run_warn_continues_and_preserves_resource_warning() -> None:
    result = run_source(
        _SOURCE,
        stdout=io.StringIO(),
        resource_profile=_profile("Warn"),
        resource_estimate=_over_limit_estimate(),
    )

    assert result.compile_ok, result.diagnostics
    assert any(
        diagnostic.get("code") == "SIMULATOR_RESOURCE_WARNING"
        for diagnostic in result.diagnostics
    )
    assert result.eval.measure is not None


def test_local_run_abort_stops_before_evaluator() -> None:
    def evaluator_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("resource rejection must precede evaluator execution")

    with _patched("compiler.staqex.run.Evaluator.run_unit", evaluator_must_not_run):
        result = run_source(
            _SOURCE,
            stdout=io.StringIO(),
            resource_profile=_profile("Abort"),
            resource_estimate=_over_limit_estimate(),
        )

    assert result.compile_ok is False
    assert any(
        diagnostic.get("code") == "SIMULATOR_RESOURCE_ERROR"
        for diagnostic in result.diagnostics
    )


def test_qasm_emission_rejects_before_lowering_even_when_policy_is_warn() -> None:
    compiled = compile_source(_SOURCE)
    assert compiled.ok and compiled.unit is not None, compiled.diagnostics

    def lowering_must_not_run(*args: object, **kwargs: object) -> object:
        raise AssertionError("resource rejection must precede QASM lowering")

    with _patched(
        "compiler.staqex.backend.qasm.emitter.lower_unit_to_circuit",
        lowering_must_not_run,
    ):
        emitted = OpenQASM3Generator(route=False).generate_detailed(
            compiled.unit,
            resource_profile=_profile("Warn"),
            resource_estimate=_over_limit_estimate(),
        )

    assert emitted.ok is False
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "SIMULATOR_RESOURCE_ERROR"


if __name__ == "__main__":
    _failed = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
            except AssertionError as _error:
                _failed += 1
                print(f"FAIL: {_name}: {_error}")
            else:
                print(f"PASS {_name}")
    raise SystemExit(1 if _failed else 0)
