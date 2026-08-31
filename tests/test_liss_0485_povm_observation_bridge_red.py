"""AT-TDD Phase 1 Red: LISS-0485 POVM observation bridge."""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source


SPEC = REPO / "docs/specs/staqex-v1-quantum-mental-model-follow-up.md"


def test_povm_bridge_spec_separates_validity_lane_and_result_evidence() -> None:
    text = SPEC.read_text(encoding="utf-8")

    assert "### 5.8 LISS-0485 POVM observation bridge design" in text
    for evidence in (
        "effect-set ID",
        "completeness/positivity status",
        "`StaticKernel` vs `HostProtocol`",
        "post-state identity",
        "`MeasurementEnvelope<T>`",
    ):
        assert evidence in text


def test_terminal_povm_preserves_request_and_measurement_evidence_in_ir() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Qubit> psi = |0>
            POVM<Qubit> z_basis = ComputationalBasis()
            Measure psi with z_basis
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    ir = compiled.scientific_semantic_ir
    assert ir is not None
    evidence = ir.povm_observation_requests["psi"]
    assert evidence["effect_set_id"] == "z_basis"
    assert evidence["state_domain"] == "Qubit"
    assert evidence["lane"] == "StaticKernel"
    assert evidence["sampling"] is True
    assert evidence["collapse"] is True
    assert evidence["post_state_identity"]
    assert evidence["provenance"]["source_id"]


def test_povm_rejection_preserves_reason_without_repair_or_fabricated_outcome() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            POVM<Position> position_basis = ComputationalBasis()
            Measure rho with position_basis
        }
        """
    )

    assert not compiled.ok
    rejection = compiled.povm_observation_rejections[0]
    assert rejection["code"] == "POVM_DOMAIN_MISMATCH"
    assert rejection["requested_effect_set"] == "position_basis"
    assert rejection["state_domain"] == "Qubit"
    assert rejection["repaired"] is False
    assert rejection["fabricated_outcome"] is False

