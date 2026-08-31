"""AT-TDD Phase 1 Red: LISS-0482 observation-to-semantic-IR mapping."""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source


SPEC = REPO / "docs/specs/staqex-v1-quantum-mental-model-follow-up.md"


def test_observation_mapping_matrix_declares_all_required_evidence() -> None:
    text = SPEC.read_text(encoding="utf-8")

    assert "### 5.5 LISS-0482 observation-to-IR mapping matrix" in text
    for role in (
        "`ExpectationProjection`",
        "`Projection`",
        "`DiagnosticView`",
        "`ReducedState`",
        "`Measurement`",
        "`DynamicMeasurement`",
        "`ObservationProtocolRequest`",
    ):
        assert role in text
    for evidence in (
        "`role`",
        "`lane`",
        "`source_id`",
        "`provenance`",
        "`exactness`",
        "`dimensions`",
    ):
        assert evidence in text


def test_inspection_mapping_preserves_role_lane_and_source_evidence() -> None:
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
    ir = compiled.scientific_semantic_ir
    assert ir is not None
    mapping = ir.observation_mappings["view"]
    assert mapping["role"] == "DiagnosticView"
    assert mapping["lane"] == "StaticKernel"
    assert mapping["source_id"]
    assert mapping["provenance"]
    assert mapping["exactness"]
    assert mapping["dimensions"]


def test_projection_loss_is_explicit_and_never_a_fabricated_finite_artifact() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            State reduced = trace_out(psi, q0)
            Measure reduced
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    ir = compiled.scientific_semantic_ir
    assert ir is not None
    mapping = ir.observation_mappings["reduced"]
    assert mapping["role"] == "ReducedState"
    assert mapping["projection_loss"] is not None
    assert mapping["finite_artifact"] is False
