"""LISS-0243: S01 tonight JobResult → TonightTicket export (AT-TDD)."""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_HOST = _REPO / "examples/showcase/S01_quantum_disaster_response/host"
if str(_HOST) not in sys.path:
    sys.path.insert(0, str(_HOST))

_ENTRY = (
    _REPO
    / "examples/showcase/S01_quantum_disaster_response/main_disaster_response.sqx"
)

from compiler.staqex.host import JobResult, MeasurementEnvelope, run_path  # noqa: E402


def test_spine_source_has_no_inspect_or_identity_evolve_times() -> None:
    text = _ENTRY.read_text(encoding="utf-8")
    assert "inspect(" not in text
    assert "evolve times" not in text

    result = run_path(str(_ENTRY), settings={"seed": 0}, stdout=io.StringIO())
    assert result.status == "succeeded"
    assert result.measurements, "expected a terminal MeasurementEnvelope"
    envelope = result.measurements[-1]
    assert envelope.vacuum is False
    assert envelope.value is not None or envelope.marginal


def test_build_tonight_ticket_happy_path_schema() -> None:
    from ticket_dto import build_tonight_ticket

    result = run_path(str(_ENTRY), settings={"seed": 0}, stdout=io.StringIO())
    ticket = build_tonight_ticket(
        result,
        entry=str(_ENTRY),
        seed=0,
        target="local",
    )
    assert ticket["schema_version"] == 1
    assert ticket["honesty"]["live_qpu"] is False
    assert ticket["honesty"]["execution"] == "sim-only"
    assert ticket["honesty"]["optimality_claim"] is False
    assert ticket["plan"]["vacuum"] is False
    assert ticket["plan"]["sample_value"] is not None
    assert ticket["job"]["status"] == "succeeded"
    assert ticket["job"]["seed"] == 0
    assert ticket["provenance"]["tool"] == "s01-host-export"
    assert "generated_at" in ticket["provenance"]
    codes = {d.get("code") for d in ticket["diagnostics"]}
    assert codes  # soft QPU / QSEM diags may remain; do not invent a clean story


def test_build_tonight_ticket_vacuum_fail_closed() -> None:
    from ticket_dto import IncompleteMeasurementError, build_tonight_ticket

    vacuum = JobResult(
        status="succeeded",
        measurements=(
            MeasurementEnvelope(
                value=None,
                marginal={},
                vacuum=True,
                sink=None,
                output="",
            ),
        ),
        diagnostics=({"code": "SOFT_DIAG", "message": "keep me"},),
        metadata={"target": "local"},
    )
    with pytest.raises(IncompleteMeasurementError):
        build_tonight_ticket(
            vacuum,
            entry=str(_ENTRY),
            seed=0,
            target="local",
        )


def test_build_tonight_ticket_empty_measurements_fail_closed() -> None:
    from ticket_dto import IncompleteMeasurementError, build_tonight_ticket

    empty = JobResult(status="succeeded", measurements=())
    with pytest.raises(IncompleteMeasurementError):
        build_tonight_ticket(empty, entry=str(_ENTRY), seed=0)


def test_export_tonight_ticket_cli_writes_json(tmp_path: Path) -> None:
    from export_tonight_ticket import export_tonight_ticket

    out = tmp_path / "tonight_ticket.json"
    exit_code = export_tonight_ticket(
        entry=str(_ENTRY),
        seed=0,
        out_path=out,
    )
    assert exit_code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["plan"]["vacuum"] is False
    assert payload["honesty"]["live_qpu"] is False
    assert payload["plan"]["sample_value"] is not None


def test_export_tonight_ticket_cli_incomplete_nonzero(tmp_path: Path) -> None:
    from export_tonight_ticket import export_tonight_ticket_from_result

    vacuum = JobResult(
        status="succeeded",
        measurements=(
            MeasurementEnvelope(
                value=None,
                marginal={},
                vacuum=True,
                sink=None,
                output="",
            ),
        ),
    )
    out = tmp_path / "incomplete.json"
    exit_code = export_tonight_ticket_from_result(
        vacuum,
        entry=str(_ENTRY),
        seed=0,
        out_path=out,
    )
    assert exit_code != 0
    # Fail-closed: do not write a success ticket with invented sample_value.
    assert not out.exists()


def test_pauli_evolve_preserves_sibling_joint_coords() -> None:
    """Single-wire Pauli evolve must not wipe unrelated joint coordinates."""
    from compiler.staqex.pipeline import compile_source
    from compiler.staqex.runtime.evaluator import Evaluator

    source = """
        package t
        pub fn main() -> Unit {
            state plan = |0>
            state fuel = |0>
            state fuel = evolve { fuel under X for pi / 2.0 until converged(fuel) max 64 }.run()
            measure plan
        }
        """
    compiled = compile_source(source)
    assert compiled.unit is not None
    result = Evaluator(seed=0).run_unit(compiled.unit, stdout=io.StringIO())
    assert result.measure is not None
    assert result.measure.vacuum is False
    assert "plan" in {k for w in result.joint.worlds for k in w.assign}