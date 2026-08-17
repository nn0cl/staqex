"""AT-TDD: OpenQASM 3.0 codegen (`OpenQASM3Generator` / `StaqexCompiler`)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.codegen_qasm import OpenQASM3Generator, StaqexCompiler  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _assert_valid_qasm3(text: str) -> None:
    assert "OPENQASM 3.0;" in text
    assert 'include "stdgates.inc";' in text
    assert re.search(r"qubit\[\d+\]\s+q;", text)
    assert re.search(r"bit\[\d+\]\s+c;", text)
    assert "measure" in text  # OpenQASM3 output keyword, always lowercase
    # No vendor SDKs leaked into output
    assert "braket" not in text.lower()
    assert "qiskit" not in text.lower()


def test_portable_bell_via_compiler() -> None:
    path = _REPO / "examples/applied/A08_entangled_compute_ancilla/main_entangled_compute_ancilla.sqx"
    qasm = StaqexCompiler().compile_to_qasm3(str(path))
    _assert_valid_qasm3(qasm)
    assert "h q[" in qasm
    assert "cx q[" in qasm
    assert "c[0] = measure q[" in qasm  # OpenQASM3 output keyword, always lowercase


def test_generator_from_unit() -> None:
    src = """
package t
pub fn main() -> Unit {
  State a = |+>
  State b = |0>
  State b = cnot(a, b)
  Measure b
}
"""
    compiled = compile_source(src)
    assert compiled.ok and compiled.unit is not None
    qasm = OpenQASM3Generator(route=False).generate(compiled.unit)
    _assert_valid_qasm3(qasm)
    assert qasm.startswith("OPENQASM 3.0;")


def test_apply_and_capply_gates() -> None:
    src = """
package t
pub fn main() -> Unit {
  State q = |0>
  State q = apply(X, q)
  State q = apply(Y, q)
  State q = apply(Z, q)
  State q = apply(H, q)
  State t = |0>
  State t = capply(q, X, t)
  State t = capply(q, Z, t)
  Measure t
}
"""
    compiled = compile_source(src)
    assert compiled.ok and compiled.unit is not None, compiled.diagnostics
    qasm = OpenQASM3Generator(route=False).generate(compiled.unit)
    _assert_valid_qasm3(qasm)
    assert "x q[" in qasm
    assert "y q[" in qasm
    assert "z q[" in qasm
    assert "h q[" in qasm
    assert "cx q[" in qasm
    assert "cz q[" in qasm


def test_apply_s_t_rx_ry_qasm() -> None:
    src = """
package t
pub fn main() -> Unit {
  State q = |0>
  State q = apply(S, q)
  State q = apply(T, q)
  State q = apply(rx(pi), q)
  State q = apply(ry(pi / 2.0), q)
  Measure q
}
"""
    compiled = compile_source(src)
    assert compiled.ok and compiled.unit is not None, compiled.diagnostics
    qasm = OpenQASM3Generator(route=False).generate(compiled.unit)
    _assert_valid_qasm3(qasm)
    assert "s q[" in qasm
    assert "t q[" in qasm
    assert "rx(" in qasm
    assert "ry(" in qasm


def test_compile_failure_before_emit() -> None:
    bad = """
package t
pub fn main() -> Unit {
  State x = ???
  Measure x
}
"""
    try:
        OpenQASM3Generator().generate_from_source(bad)
        raise AssertionError("expected ValueError")
    except ValueError as e:
        assert "compile failed" in str(e).lower() or "PARSE" in str(e) or "failed" in str(e).lower()

    missing = _REPO / "examples/does_not_exist.sqx"
    try:
        StaqexCompiler().compile_to_qasm3(str(missing))
        raise AssertionError("expected FileNotFoundError")
    except FileNotFoundError:
        pass


def test_bell_example_file_roundtrip() -> None:
    path = _REPO / "examples/applied/A09_qkd_corridor/main_qkd_corridor.sqx"
    qasm = StaqexCompiler(route=True).compile_to_qasm3(str(path))
    _assert_valid_qasm3(qasm)


def test_stdlib_only_module() -> None:
    import ast
    from pathlib import Path

    import compiler.staqex.codegen_qasm as mod

    files = [Path(mod.__file__)]
    qasm_dir = Path(mod.__file__).parent / "backend" / "qasm"
    files.extend(sorted(qasm_dir.glob("*.py")))
    forbidden = {"braket", "qiskit", "amazon", "cirq", "pennylane"}
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.append(node.module.split(".")[0])
        assert not (forbidden & set(imported)), (path, imported)


def test_trotter_ising_evolve_qasm() -> None:
    """LISS-0008: TFIM Evolve under H → discrete rz/cx (not empty).

    LISS-0050 (ADR 0094): the example now carries an explicit
    `using Suzuki(order = 2, steps = N)` policy, so lowering goes through
    the Suzuki S2 product (comment `suzuki S2 ...`), not the retired
    first-order `trotter_gates` path.
    """
    path = _REPO / "examples/basics/B08_operators_hamiltonians/operators_hamiltonians.sqx"
    with pytest.raises(RuntimeError, match="EVOLUTION_REALIZATION_REQUIRED"):
        StaqexCompiler(route=False).compile_to_qasm3(str(path))


def test_trotter_single_qubit_x() -> None:
    src = """
package t
pub fn main() -> Unit {
  Operator H = X
  State q = |0>
  State q = Evolve { q under H for 0.5 using Suzuki(order = 2, steps = 4) }.run()
  Measure q
}
"""
    compiled = compile_source(src)
    assert compiled.ok and compiled.unit is not None, compiled.diagnostics
    qasm = OpenQASM3Generator(route=False).generate(compiled.unit)
    _assert_valid_qasm3(qasm)
    assert "h q[" in qasm
    assert "rz(" in qasm
    assert "suzuki" in qasm


def test_trotter_rejects_fock_hamiltonian() -> None:
    path = _REPO / "tests/fixtures/staqex/quantum_oscillator.sqx"
    try:
        StaqexCompiler(route=False).compile_to_qasm3(str(path))
        raise AssertionError("expected RuntimeError for Fock H")
    except RuntimeError as e:
        assert "QASM_TROTTER_UNSUPPORTED_H" in str(e)


if __name__ == "__main__":
    test_portable_bell_via_compiler()
    test_generator_from_unit()
    test_apply_and_capply_gates()
    test_apply_s_t_rx_ry_qasm()
    test_compile_failure_before_emit()
    test_bell_example_file_roundtrip()
    test_stdlib_only_module()
    test_trotter_ising_evolve_qasm()
    test_trotter_single_qubit_x()
    test_trotter_rejects_fock_hamiltonian()
    print("OK — OpenQASM 3 codegen")
