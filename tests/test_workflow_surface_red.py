"""AT-TDD Phase 1 Red: declarative Workflow surface (ADR 0073)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_workflow_declarations_resolve_independently_of_source_order() -> None:
    compiled = compile_source(
        """
        package t
        workflow GroundStateSweep {
            until energy <= 0.01
            observable energy
            parameter theta : Param<Angle>
            experiment = GroundState
        }
        theory Ising { Operator H = X + Z }
        experiment GroundState { theory = Ising }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.workflow_contracts is not None
    contract = compiled.workflow_contracts["GroundStateSweep"]
    assert contract.experiment == "GroundState"
    assert contract.parameters == ("theta",)
    assert contract.parameter_types == ("Param<Angle>",)
    assert contract.observables == ("energy",)
    assert contract.until == "energy <= 0.01"


def test_workflow_declares_named_host_update_callback() -> None:
    compiled = compile_source(
        """
        package t
        workflow GroundStateSweep {
            experiment = GroundState
            parameter theta : Param<Angle>
            observable energy
            update = next_theta
            until energy <= 0.01
        }
        experiment GroundState { theory = Ising }
        theory Ising { Operator H = X + Z }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.workflow_contracts["GroundStateSweep"].update == "next_theta"


def test_workflow_cannot_reference_provider_or_kernel_job_values() -> None:
    codes = _codes(
        """
        package t
        workflow Invalid {
            experiment = GroundState
            observable Job
            backend = ProviderSdk
        }
        theory Ising { Operator H = X + Z }
        experiment GroundState { theory = Ising }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "WORKFLOW_SURFACE_ERROR" in codes


def test_workflow_validates_experiment_param_type_and_until_target() -> None:
    codes = _codes(
        """
        package t
        workflow Invalid {
            experiment = MissingExperiment
            parameter theta : Host<Float>
            observable energy
            until unknown <= 0.01
        }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "WORKFLOW_SURFACE_ERROR" in codes


def test_workflow_rejects_non_comparison_until_expression() -> None:
    codes = _codes(
        """
        package t
        workflow Invalid {
            experiment = GroundState
            observable energy
            until Job.result()
        }
        experiment GroundState { theory = Ising }
        theory Ising { Operator H = X + Z }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "WORKFLOW_SURFACE_ERROR" in codes


def test_workflow_rejects_inline_update_expression() -> None:
    codes = _codes(
        """
        package t
        workflow Invalid {
            experiment = GroundState
            parameter theta : Param<Angle>
            observable energy
            update = theta + 0.1
        }
        experiment GroundState { theory = Ising }
        theory Ising { Operator H = X + Z }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "WORKFLOW_SURFACE_ERROR" in codes


if __name__ == "__main__":
    test_workflow_declarations_resolve_independently_of_source_order()
    test_workflow_declares_named_host_update_callback()
    test_workflow_cannot_reference_provider_or_kernel_job_values()
    test_workflow_validates_experiment_param_type_and_until_target()
    test_workflow_rejects_non_comparison_until_expression()
    test_workflow_rejects_inline_update_expression()
    print("OK — workflow surface Red tests")
