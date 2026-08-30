"""AT-TDD Phase 1 Red: LISS-0481 typed observation contract."""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source


SPEC = REPO / "docs/specs/staqex-v1-quantum-mental-model-follow-up.md"


def test_observation_matrix_declares_lane_sampling_collapse_and_provenance() -> None:
    text = SPEC.read_text(encoding="utf-8")

    assert "### 5.4 LISS-0481 observation contract matrix" in text
    for operation in (
        "`expect(O, state)`",
        "`project(P, state)`",
        "`inspect(state)`",
        "`trace_out(state, subsystem)`",
        "terminal `measure(state)`",
        "`tomography(plan)`",
    ):
        assert operation in text
    for field in ("Collapse", "Sampling", "Lane", "Required provenance", "Unsupported behavior"):
        assert field in text


def test_inspect_and_measure_expose_distinct_observation_contract_metadata() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            State view = Inspect(psi)
            Measure view
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.scientific_semantic_ir is not None
    ir = compiled.scientific_semantic_ir
    assert ir.observation_contracts["view"]["kind"] == "DiagnosticView"
    assert ir.observation_contracts["view"]["collapse"] is False
    assert ir.observation_contracts["view"]["source_id"]
    assert ir.measurement_envelopes["view"]["collapse"] is True


def test_tomography_in_static_kernel_fails_without_a_fabricated_report() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Observation<T> report = tomography(plan)
            Measure report
        }
        """
    )

    assert not compiled.ok
    unsupported = [
        diagnostic
        for diagnostic in compiled.diagnostics
        if diagnostic.get("code") == "OBSERVATION_UNSUPPORTED"
    ]
    assert len(unsupported) == 1
    assert unsupported[0]["operation"] == "tomography"
    assert unsupported[0]["lane"] == "StaticKernel"
    assert not hasattr(compiled, "observation_report")
