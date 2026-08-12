"""AT-TDD tests for LISS-0020 / A10 mission observatory capstone (v2 catalog)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))
_SV_ROOT = _REPO / "tests/spec_verification"
if str(_SV_ROOT) not in sys.path:
    sys.path.insert(0, str(_SV_ROOT))

from compiler.staqex.codegen_qasm import StaqexCompiler  # noqa: E402
from compiler.staqex.pipeline import compile_path  # noqa: E402
from compiler.staqex.run import run_path  # noqa: E402
from tests.spec_verification.suites.sv09_examples import EXAMPLES  # noqa: E402


_CAPSTONE = _REPO / "examples/applied/A10_mission_observatory"
_ENTRY = _CAPSTONE / "main_mission_observatory.sqx"
_QPU_ENTRY = _REPO / "examples/basics/B11_qft_registers/main_qft_registers.sqx"


def test_capstone_module_graph_and_readmes_exist() -> None:
    expected = [
        _CAPSTONE / "README.md",
        _CAPSTONE / "domain/observatory_config.sqx",
        _CAPSTONE / "domain/topology.sqx",
        _CAPSTONE / "domain/link_parties.sqx",
        _CAPSTONE / "operators/ssh_hamiltonian.sqx",
        _CAPSTONE / "operators/bell_channel.sqx",
        _ENTRY,
    ]
    missing = [str(path.relative_to(_REPO)) for path in expected if not path.is_file()]
    assert not missing, f"missing capstone module graph: {missing}"


def test_capstone_is_registered_as_an_official_example() -> None:
    assert ("applied/A10_mission_observatory", "main_mission_observatory.sqx") in EXAMPLES


def test_capstone_cpu_entry_compiles_and_reaches_terminal_measure() -> None:
    compiled = compile_path(_ENTRY)
    assert compiled.ok, compiled.diagnostics

    result = run_path(_ENTRY, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None or result.eval.joint.is_vacuum()


def test_capstone_qpu_lane_emits_portable_openqasm3() -> None:
    qasm = StaqexCompiler(route=True).compile_to_qasm3(str(_QPU_ENTRY))
    assert qasm.startswith("OPENQASM 3.0;")
    assert 'include "stdgates.inc";' in qasm
    assert "qubit[" in qasm
    assert "measure" in qasm  # OpenQASM3 output keyword, always lowercase
    assert "braket" not in qasm.lower()
    assert "qiskit" not in qasm.lower()


def test_capstone_readme_contains_slim_integration_honesty() -> None:
    readme = (_CAPSTONE / "README.md").read_text(encoding="utf-8")
    for term in (
        "Honesty",
        "slim",
        "Bell",
        "SSH",
        "kitchen sink",
    ):
        assert term in readme, f"README missing capstone term: {term}"


if __name__ == "__main__":
    import traceback

    tests = [
        test_capstone_module_graph_and_readmes_exist,
        test_capstone_is_registered_as_an_official_example,
        test_capstone_cpu_entry_compiles_and_reaches_terminal_measure,
        test_capstone_qpu_lane_emits_portable_openqasm3,
        test_capstone_readme_contains_slim_integration_honesty,
    ]
    failures = 0
    for test in tests:
        try:
            test()
        except Exception:  # noqa: BLE001 - simple standalone test runner
            failures += 1
            traceback.print_exc()
    if failures:
        raise SystemExit(f"{failures}/{len(tests)} capstone tests failed")
    print("OK — A10 mission observatory capstone")
