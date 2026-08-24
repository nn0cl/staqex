"""Phase 1 Red contracts for the S02 example boundary inventory."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

EXAMPLE_DIR = REPO / "examples/showcase/S02_drug_discovery"
README = EXAMPLE_DIR / "README.md"
SOURCE = EXAMPLE_DIR / "main_selection.sqx"


def test_s02_readme_names_all_four_boundary_stages_and_partial_scope() -> None:
    """The researcher-facing inventory must classify the example honestly."""

    readme = README.read_text(encoding="utf-8")

    assert "Blackboard equation" in readme
    assert "Ideal Staqex expression" in readme
    assert "Explicit finite realization" in readme
    assert "QPU/QASM projection" in readme
    assert "Classification: partial" in readme


def test_s02_readme_records_the_actual_finite_target_boundary() -> None:
    """Documentation must preserve ideal meaning while naming target rejection."""

    readme = README.read_text(encoding="utf-8")

    assert "QASM_TROTTER_UNSUPPORTED_H" in readme
    assert "capability-rejected" in readme
    assert "submitted=False" in readme
    assert "no live QPU" in readme


def test_s02_source_keeps_exact_and_finite_lanes_distinct() -> None:
    """The source must expose Realize separately from exact local evolution."""

    source = SOURCE.read_text(encoding="utf-8")

    assert "Operator U_t = exp(-i * H_obj * dur / hbar)" in source
    assert "State psi_final = Evolve() { U_t * psi_sel }.run()" in source
    assert 'Operator U_formal = Limit N -> Infinity' in source
    assert 'Operator U_qpu = Realize(' in source
    assert 'method = "suzuki"' in source
    assert "order = 2" in source
    assert "steps = 8" in source
    assert "error_budget = 1e-6" in source


def test_s02_finite_target_rejection_is_atomic_and_provider_free() -> None:
    """Current target lowering must remain diagnostic-only and fail closed."""

    host = EXAMPLE_DIR / "host"
    sys.path.insert(0, str(host))
    try:
        from benchmark_report import _explicit_evolution_comparison
    finally:
        sys.path.remove(str(host))

    comparison = _explicit_evolution_comparison()

    assert comparison["exact_local"]["operator"] == "U_t"
    assert comparison["finite_target"]["operator"] == "U_qpu"
    assert comparison["finite_target"]["execution"] == "target-plan-only"
    assert comparison["finite_target"]["submitted"] is False
    assert comparison["finite_target"]["status"] == "capability-rejected"
    assert comparison["capability_rejection"] == "QASM_TROTTER_UNSUPPORTED_H"
    assert comparison["partial_program"] is None
    assert comparison["target_plan_provenance"] is None


if __name__ == "__main__":
    for test in (
        test_s02_readme_names_all_four_boundary_stages_and_partial_scope,
        test_s02_readme_records_the_actual_finite_target_boundary,
        test_s02_source_keeps_exact_and_finite_lanes_distinct,
        test_s02_finite_target_rejection_is_atomic_and_provider_free,
    ):
        test()
