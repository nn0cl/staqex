"""Coverage checks for A10 slim mission observatory (v2 catalog)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_CAPSTONE = _REPO / "examples/applied/A10_mission_observatory"


def _source(relative: str) -> str:
    return (_CAPSTONE / relative).read_text(encoding="utf-8")


def test_slim_capstone_cpu_narrative_covers_integration_slice() -> None:
    main = _source("main_mission_observatory.sqx")
    for form in ("Evolve", "Inspect(", "cnot(", "expect(ZZ", "QubitRegister<3>"):
        assert form in main, f"A10 CPU narrative missing form: {form}"


def test_slim_capstone_modules_use_distinct_physics_operations() -> None:
    expected = {
        "operators/ssh_hamiltonian.sqx": ("hop(", "build_ssh_hamiltonian"),
        "operators/bell_channel.sqx": ("build_link_witness",),
    }
    for relative, forms in expected.items():
        source = _source(relative)
        for form in forms:
            assert form in source, f"{relative} missing operation: {form}"


def test_slim_capstone_readme_states_non_kitchen_sink_boundary() -> None:
    readme = _source("README.md")
    for term in ("kitchen sink", "Honesty", "B12", "A06", "A09"):
        assert term in readme, f"A10 README missing boundary term: {term}"


def test_slim_capstone_keeps_one_terminal_measurement_boundary() -> None:
    main = _source("main_mission_observatory.sqx")
    assert main.count("Measure ") == 1
    assert main.rstrip().endswith("Measure probe tracing_out site\n}")
