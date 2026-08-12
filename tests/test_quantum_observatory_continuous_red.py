"""Open-system and continuous-model boundaries after legacy observatory retirement."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_FIXTURES = _REPO / "tests/fixtures/staqex"


def test_fixture_continuous_models_remain_available_for_sv() -> None:
    for name in ("quantum_oscillator.sqx", "grid_oscillator.sqx"):
        path = _FIXTURES / name
        assert path.is_file(), f"missing fixture {path}"
        text = path.read_text(encoding="utf-8")
        assert "Evolve" in text, f"{name} should exercise Evolve"


def test_open_system_examples_cover_lindblad_lane() -> None:
    for rel in (
        "examples/basics/B12_open_systems/main_open_systems.sqx",
        "examples/applied/A07_open_system_sensor/main_open_system_sensor.sqx",
    ):
        text = (_REPO / rel).read_text(encoding="utf-8")
        assert "lindblad(" in text, f"{rel} should demonstrate lindblad"
