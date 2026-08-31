"""AT-TDD Phase 1 Red: LISS-0484 broader observation algebra."""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source


SPEC = REPO / "docs/specs/staqex-v1-quantum-mental-model-follow-up.md"


def test_observation_algebra_spec_declares_composition_laws_and_evidence() -> None:
    text = SPEC.read_text(encoding="utf-8")

    assert "### 5.7 LISS-0484 broader observation algebra design" in text
    for law in (
        "`expect(project(P, state))`",
        "`inspect(project(P, state))`",
        "`trace_out(project(P, state))`",
        "operation kind",
        "lineage",
        "projection-loss",
        "capability status",
    ):
        assert law in text


def test_inspect_algebra_preserves_non_sampling_lineage_and_operation_kind() -> None:
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
    algebra = ir.observation_algebra["view"]
    assert algebra["operation_kind"] == "inspect"
    assert algebra["lane"] == "StaticKernel"
    assert algebra["sampling"] is False
    assert algebra["collapse"] is False
    assert algebra["lineage"]["source_id"]
    assert algebra["lineage"]["input"] == "psi"


def test_trace_out_algebra_records_projection_loss_without_finite_artifact() -> None:
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
    algebra = ir.observation_algebra["reduced"]
    assert algebra["operation_kind"] == "trace_out"
    assert algebra["sampling"] is False
    assert algebra["collapse"] is False
    assert algebra["projection_loss"]
    assert algebra["finite_artifact"] is False


def test_nested_observation_keeps_outer_and_inner_operation_evidence() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            State view = Inspect(Inspect(psi))
            Measure view
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    ir = compiled.scientific_semantic_ir
    assert ir is not None
    algebra = ir.observation_algebra["view"]
    assert algebra["operation_kind"] == "inspect"
    assert algebra["composition"]["outer"] == "inspect"
    assert algebra["composition"]["inner"] == "inspect"
    assert algebra["composition"]["sampling"] is False

