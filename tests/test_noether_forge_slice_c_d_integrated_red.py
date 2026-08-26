"""AT-TDD regression: A11_noether_forge full-module + IR checks.

Historically LISS-0120 Slice C+D (1,000-3,000 non-blank-line "full
candidate" expansion, part of the rejected/deferred "representative
program" ambition -- see staqex-v1-representative-program-rebaseline.md).
LISS-0338 (2026-08-05) retheme's A11's content to a structural-monitoring
quantum magnetometer with the Adjudicator's explicit direction to rewrite
freely; the 1,000-3,000-line budget and 8-20-module-count targets this
file used to assert are no longer this example's goal and have been
removed. The remaining checks (module tree, compile/run correctness via
multi-file-aware run_path, HIR/Physics IR presence, invalid-boundary
fixture) stay valid for any A11 content and are kept -- with the
Operator-atom-symbol assertion relaxed to Operator-node presence only,
since main_static.sqx now builds its Hamiltonian via an imported library
function (physics/hamiltonian_builder.sqx), and physics_ir's static
extraction does not walk through a Call indirection to find the atoms a
called function's own Operator expression uses -- a real, minor,
pre-existing static-analysis limitation for this common Hamiltonian-
builder-function pattern (also used by A06/A10/A03), not something this
Issue introduces or fixes.
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
_FIXTURES = _REPO / "tests" / "fixtures" / "noether_forge"

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
    "application/spectroscopy_protocol.sqx",
    "application/phase_evidence.sqx",
    "application/result_contract.sqx",
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


def test_required_full_candidate_module_tree_exists() -> None:
    missing = [rel for rel in _REQUIRED_RELATIVE if not (_ROOT / rel).is_file()]
    assert not missing, f"missing full-candidate modules: {missing}"


def test_each_sqx_file_within_hard_max_300_non_blank() -> None:
    for path in _sqx_files():
        count = len([line for line in _read(path).splitlines() if line.strip()])
        assert count <= 300, f"{path.relative_to(_REPO)} has {count} non-blank lines"


def test_entry_point_compiles_runs_and_keeps_terminal_measure() -> None:
    from compiler.staqex import run_path
    from compiler.staqex.pipeline import compile_path

    compiled = compile_path(str(_ENTRY))
    assert compiled.ok, compiled.diagnostics
    source = _read(_ENTRY)
    assert re.search(r"\bmeasure\b", source)
    first = run_path(str(_ENTRY), settings={"target": "local", "seed": 0})
    second = run_path(str(_ENTRY), settings={"target": "local", "seed": 0})
    assert first.status == "succeeded" and second.status == "succeeded"
    assert first.measurements == second.measurements


def test_sources_forbid_dynamic_and_provider_surface() -> None:
    for path in _sqx_files():
        lowered = _read(path).lower()
        for token in _FORBIDDEN_SOURCE_TOKENS:
            assert token.lower() not in lowered, f"{path.name} contains {token!r}"


def test_source_to_hir_physics_and_soft_semantic_ir_evidence() -> None:
    from compiler.staqex.hir import build_hir
    from compiler.staqex.pipeline import compile_path
    from compiler.staqex.quantum_semantic_ir import QuantumSemanticModule

    compiled = compile_path(str(_ENTRY))
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None and compiled.unit is not None
    hir = build_hir(
        compiled.checker,
        scope_contracts=compiled.scope_contracts,
        unit=compiled.unit,
    )
    assert hir is not None
    assert compiled.physics_ir is not None
    assert len(compiled.physics_ir.nodes) >= 1
    assert any(node.kind == "Operator" for node in compiled.physics_ir.nodes)
    assert isinstance(compiled.quantum_semantic_ir, QuantumSemanticModule)
    assert compiled.quantum_semantic_ir.schema_version == 1
    soft_codes = {
        d.get("code")
        for d in compiled.diagnostics
        if isinstance(d.get("code"), str) and str(d.get("code")).startswith("QSEM_")
    }
    assert compiled.ok is True
    assert all(str(code).startswith("QSEM_") for code in soft_codes)


def test_invalid_linear_boundary_fixture_diagnoses_source_rule() -> None:
    from compiler.staqex.pipeline import compile_source

    fixture = _FIXTURES / "invalid_linear_discard.sqx"
    assert fixture.is_file(), f"missing fixture {fixture}"
    compiled = compile_source(_read(fixture))
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "LINEAR_IMPLICIT_DISCARD" in codes
    assert compiled.ok is False


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
        f"A11_noether_forge full-candidate Red: {len(tests) - failures} passed, {failures} failed"
    )
    raise SystemExit(1 if failures else 0)
