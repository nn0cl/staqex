"""AT-TDD: LISS-0350 -- fix Jordan-Wigner mapping's absolute zero/Hermitian
tolerances in second_quantization.py (fixes A03_h2_vqe's silently-zeroed
electronic Hamiltonian).

Design decision: docs/issues/LISS-0350-jw-mapping-scale-relative-tolerances.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import io  # noqa: E402

from compiler.staqex import run_path  # noqa: E402
from compiler.staqex.ast_nodes import OpLit  # noqa: E402
from compiler.staqex.runtime import hamiltonian as ham_mod  # noqa: E402

_A03_PATH = str(_REPO / "examples/applied/A03_h2_vqe/main_h2_vqe.sqx")


def test_h2_electronic_hamiltonian_is_not_silently_zeroed() -> None:
    """The JW-mapped H_electronic must not collapse to a bare OpLit(0.0).

    Real-unit Joule-scale coefficients (~1e-18) must survive
    jordan_wigner_map's zero-drop filter, which used to compare against a
    fixed absolute epsilon (1e-12) six orders of magnitude larger than the
    coefficients themselves.
    """
    seen_ops: list[object] = []
    orig = ham_mod.op_n_qubits

    def traced(op, env, scalars=None):
        seen_ops.append(env.get("H_electronic"))
        return orig(op, env, scalars)

    ham_mod.op_n_qubits = traced
    try:
        result = run_path(
            _A03_PATH, settings={"target": "local", "seed": 0}, stdout=io.StringIO()
        )
    finally:
        ham_mod.op_n_qubits = orig

    assert result.status == "succeeded", result.diagnostics
    assert seen_ops, "op_n_qubits was never called"
    h_electronic = seen_ops[0]
    assert not (
        isinstance(h_electronic, OpLit) and h_electronic.value == 0.0
    ), "H_electronic collapsed to a bare zero literal -- the JW mapping's zero-drop filter is dropping real physical coefficients"


def test_op_n_qubits_reports_two_qubits_for_the_combined_hamiltonian() -> None:
    seen: list[int] = []
    orig = ham_mod.op_n_qubits

    def traced(op, env, scalars=None):
        nq = orig(op, env, scalars)
        seen.append(nq)
        return nq

    ham_mod.op_n_qubits = traced
    try:
        result = run_path(
            _A03_PATH, settings={"target": "local", "seed": 0}, stdout=io.StringIO()
        )
    finally:
        ham_mod.op_n_qubits = orig

    assert result.status == "succeeded", result.diagnostics
    assert seen == [2], f"expected op_n_qubits to report 2 qubits, got {seen}"
