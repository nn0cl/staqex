"""AT-TDD regression: A11_noether_forge structural checks.

Historically LISS-0120 Slice B (300-500 non-blank-line vertical
prototype, part of the rejected/deferred 1,000-3,000-line "representative
program" ambition -- see staqex-v1-representative-program-rebaseline.md).
LISS-0338 (2026-08-05) retheme's A11's content to a structural-monitoring
quantum magnetometer with the Adjudicator's explicit direction to rewrite
freely; the line-count floor this file used to assert is no longer this
example's goal and has been removed. The remaining structural checks
(module tree, compile/run correctness, no provider/dynamic surface) stay
valid for any A11 content and are kept.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_ROOT = _REPO / "examples" / "applied" / "A11_noether_forge"
_ENTRY = _ROOT / "main_static.sqx"

_REQUIRED_RELATIVE = (
    "main_static.sqx",
    "domain/lattice.sqx",
    "domain/site.sqx",
    "domain/couplings.sqx",
    "domain/experiment_config.sqx",
    "physics/model_families.sqx",
    "physics/hamiltonian_builder.sqx",
    "physics/initial_states.sqx",
    "physics/observables.sqx",
    "physics/symmetries.sqx",
    "application/quench_protocol.sqx",
    "application/phase_evidence.sqx",
    "presentation/evidence_dossier.sqx",
)

_FORBIDDEN_SOURCE_TOKENS = (
    "provider",
    "dynamic qpu",
    "Controller<",
    "qiskit",
    "cirq",
    "pennylane",
)


def _sqx_files() -> list[Path]:
    if not _ROOT.exists():
        raise FileNotFoundError(_ROOT)
    return sorted(_ROOT.rglob("*.sqx"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_required_module_tree_exists() -> None:
    missing = [rel for rel in _REQUIRED_RELATIVE if not (_ROOT / rel).is_file()]
    assert not missing, f"missing Noether Forge modules: {missing}"


def test_each_sqx_file_within_hard_max_300_non_blank() -> None:
    for path in _sqx_files():
        count = len([line for line in _read(path).splitlines() if line.strip()])
        assert count <= 300, f"{path.relative_to(_REPO)} has {count} non-blank lines"


def test_entry_point_compiles_and_keeps_terminal_measure() -> None:
    from compiler.staqex.pipeline import compile_path

    assert _ENTRY.is_file()
    compiled = compile_path(str(_ENTRY))
    assert compiled.ok, compiled.diagnostics
    source = _read(_ENTRY)
    assert re.search(r"\bmeasure\b", source)
    assert "main" in source


def test_entry_point_runs_deterministically_with_seed() -> None:
    from compiler.staqex import run_path

    first = run_path(str(_ENTRY), settings={"target": "local", "seed": 0})
    second = run_path(str(_ENTRY), settings={"target": "local", "seed": 0})
    assert first.status == "succeeded"
    assert second.status == "succeeded"
    assert first.measurements == second.measurements


def test_sources_forbid_dynamic_and_provider_surface() -> None:
    for path in _sqx_files():
        lowered = _read(path).lower()
        for token in _FORBIDDEN_SOURCE_TOKENS:
            assert token.lower() not in lowered, f"{path.name} contains {token!r}"


def test_ownership_directories_are_present() -> None:
    for name in ("domain", "physics", "application", "presentation"):
        assert (_ROOT / name).is_dir(), name


def test_soft_semantic_ir_available_when_compiled() -> None:
    from compiler.staqex.pipeline import compile_path

    compiled = compile_path(str(_ENTRY))
    assert compiled.ok
    # Soft field from LISS-0082 Slice F; prototype must not require providers.
    assert hasattr(compiled, "quantum_semantic_ir")


if __name__ == "__main__":
    tests = tuple(
        value
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    )
    failures = 0
    for test in tests:
        try:
            test()
        except Exception as error:
            failures += 1
            print(f"FAIL {test.__name__}: {type(error).__name__}: {error}")
    print(
        f"A11_noether_forge structural Red: {len(tests) - failures} passed, {failures} failed"
    )
    raise SystemExit(1 if failures else 0)
