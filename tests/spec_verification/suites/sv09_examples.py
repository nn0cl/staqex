"""SV-09: Official physics examples — check + run regression."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_path, compile_source  # noqa: E402
from compiler.staqex.run import run_path, run_source  # noqa: E402

_BASICS = [
    ("basics/B01_never_leave_the_state", "never_leave_the_state.sqx"),
    ("basics/B02_when_not_if", "when_not_if.sqx"),
    ("basics/B03_failure_worldline", "failure_worldline.sqx"),
    ("basics/B04_evolve_not_loops", "evolve_not_loops.sqx"),
    ("basics/B05_phase_interference", "phase_interference.sqx"),
    ("basics/B06_type_first_dimensions", "type_first_dimensions.sqx"),
    ("basics/B07_structure_visibility", "structure_visibility.sqx"),
    ("basics/B08_operators_hamiltonians", "operators_hamiltonians.sqx"),
    ("basics/B09_multi_file_modules", "main_multi_file_modules.sqx"),
    ("basics/B10_static_qpu_lane", "main_static_qpu_lane.sqx"),
    ("basics/B11_qft_registers", "main_qft_registers.sqx"),
    ("basics/B12_open_systems", "main_open_systems.sqx"),
    ("basics/B13_host_job_api", "main_host_job.sqx"),
    ("basics/B14_resource_profile", "main_resource_profile.sqx"),
    ("basics/B15_multi_register", "main_multi_register.sqx"),
]

_APPLIED = [
    ("applied/A01_quantum_attention_toy", "main_quantum_attention_toy.sqx"),
    ("applied/A02_robot_graph_planner", "main_robot_graph_planner.sqx"),
    ("applied/A03_h2_vqe", "main_h2_vqe.sqx"),
    ("applied/A04_hp_protein_folding", "main_hp_protein_folding.sqx"),
    ("applied/A05_qaoa_portfolio", "main_qaoa_portfolio.sqx"),
    ("applied/A06_topological_edge_memory", "main_topological_edge_memory.sqx"),
    ("applied/A07_open_system_sensor", "main_open_system_sensor.sqx"),
    ("applied/A08_entangled_compute_ancilla", "main_entangled_compute_ancilla.sqx"),
    ("applied/A09_qkd_corridor", "main_qkd_corridor.sqx"),
    ("applied/A10_mission_observatory", "main_mission_observatory.sqx"),
    ("applied/A11_noether_forge", "main_static.sqx"),
]

EXAMPLES = _BASICS + _APPLIED

HARD = {
    "FORBIDDEN_KEYWORD",
    "EARLY_COLLAPSE_ERROR",
    "NESTED_WHEN_ERROR",
    "PARSE_ERROR",
    "LEX_ERROR",
}


def run() -> list[CaseResult]:
    out: list[CaseResult] = []
    root = _REPO / "examples"

    for folder, fname in EXAMPLES:
        path = root / folder / fname
        case_id = f"sv09-{folder.replace('/', '-')}-{fname.replace(".sqx", "")}"
        title = f"examples/{folder}/{fname}"
        try:
            if not path.is_file():
                raise AssertionFailure("PARSE_ERROR", f"missing {path}")
            # ADR 0054+: path-link when the entry imports other units
            source = path.read_text(encoding="utf-8")
            needs_link = "\nimport " in source or source.startswith("import ")
            if needs_link:
                compiled = compile_path(path)
                hard = [d for d in compiled.diagnostics if d.get("code") in HARD]
                if hard:
                    raise AssertionFailure(hard[0]["code"], str(hard))
                retired = [
                    d for d in compiled.diagnostics if d.get("code") == "RETIRED_KEYWORD"
                ]
                if retired:
                    raise AssertionFailure("RETIRED_KEYWORD", str(retired))
                buf = io.StringIO()
                result = run_path(path, seed=0, stdout=buf)
            else:
                compiled = compile_source(source)
                hard = [d for d in compiled.diagnostics if d.get("code") in HARD]
                if hard:
                    raise AssertionFailure(hard[0]["code"], str(hard))
                retired = [
                    d for d in compiled.diagnostics if d.get("code") == "RETIRED_KEYWORD"
                ]
                if retired:
                    raise AssertionFailure("RETIRED_KEYWORD", str(retired))
                buf = io.StringIO()
                result = run_source(source, seed=0, stdout=buf)
            if not result.compile_ok:
                raise AssertionFailure("PARSE_ERROR", str(result.diagnostics))
            if result.eval.measure is None and not result.eval.joint.is_vacuum():
                # must have terminal Measure outcome (Vacuum Measure OK)
                raise AssertionFailure("EARLY_COLLAPSE_ERROR", "missing Measure result")

            out.append(
                CaseResult(
                    "SV-09",
                    case_id,
                    title,
                    True,
                    ["staqex check", "staqex run"],
                )
            )
        except AssertionFailure as e:
            out.append(
                CaseResult(
                    "SV-09",
                    case_id,
                    title,
                    False,
                    error_code=e.code,
                    message=str(e),
                )
            )
        except Exception as e:  # noqa: BLE001 — surface kernel errors in report
            out.append(
                CaseResult(
                    "SV-09",
                    case_id,
                    title,
                    False,
                    error_code="UNEXPECTED_EXCEPTION",
                    message=str(e),
                )
            )

    # Index README exists
    try:
        if not (root / "README.md").is_file():
            raise AssertionFailure("PARSE_ERROR", "examples/README.md missing")
        for folder, _ in EXAMPLES:
            if not (root / folder / "README.md").is_file():
                raise AssertionFailure("PARSE_ERROR", f"{folder}/README.md missing")
        out.append(
            CaseResult(
                "SV-09",
                "sv09-docs",
                "examples READMEs present",
                True,
                ["docs"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-09",
                "sv09-docs",
                "examples READMEs",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
