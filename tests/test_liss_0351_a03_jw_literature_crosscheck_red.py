"""AT-TDD: LISS-0351 -- automate A03_h2_vqe's Jordan-Wigner literature
cross-check (the "Follow-up (not yet done)" item in
docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md).

Design decision: docs/issues/LISS-0351-a03-jw-literature-crosscheck-test.md
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import run_path  # noqa: E402
from compiler.staqex.ast_nodes import OpBin, OpPauli  # noqa: E402
from compiler.staqex.runtime import hamiltonian as ham_mod  # noqa: E402

_A03_PATH = str(_REPO / "examples/applied/A03_h2_vqe/main_h2_vqe.sqx")

# CODATA 2018 Hartree-to-Joule conversion (matches dimensions.py's own
# "Ha": ("J", 4.3597447222071e-18) unit-table entry).
_HA_TO_J = 4.3597447222071e-18

# Research note §5 / §4: fermionic parameters solved from the O'Malley et
# al. (2016) Table 1 literature coefficients (via the ENCCS reproduction),
# and the derived electronic-only g0 (§6). Tolerance is looser than the
# literature source's own 4-decimal precision to avoid brittleness.
_TOL_HA = 1e-3
_EXPECTED_HA = {
    "I": -0.4804,  # research note §6: derived electronic-only g0
    "Z0": 0.3435,  # literature g1
    "Z1": -0.4347,  # literature g2
    "Z0Z1": 0.5716,  # literature g3
    "X0X1": 0.091,  # literature g4
    "Y0Y1": 0.091,  # literature g5
}
_E_NN_HA = 0.705570  # main_h2_vqe.sqx's own nuclear_repulsion value
_LITERATURE_FULL_G0_HA = 0.2252


def _extract_h_electronic_coefficients() -> dict[str, float]:
    """Run A03, capture H_electronic's grouped Pauli-term coefficients
    (Joules), keyed by Pauli string (e.g. "Z0Z1"), converted to Hartree."""
    captured: dict[str, object] = {}
    orig = ham_mod.op_n_qubits

    def traced(op, env, scalars=None):
        if "H_electronic" in env and "H_electronic" not in captured:
            captured["H_electronic"] = env["H_electronic"]
        return orig(op, env, scalars)

    ham_mod.op_n_qubits = traced
    try:
        result = run_path(
            _A03_PATH, settings={"target": "local", "seed": 0}, stdout=io.StringIO()
        )
    finally:
        ham_mod.op_n_qubits = orig

    assert result.status == "succeeded", result.diagnostics
    assert "H_electronic" in captured, "H_electronic was never bound"
    h_electronic = captured["H_electronic"]

    def flatten_sum(e):
        if isinstance(e, OpBin) and e.op == "+":
            return flatten_sum(e.lhs) + flatten_sum(e.rhs)
        return [e]

    def pauli_str(p):
        if isinstance(p, OpPauli):
            return f"{p.kind}{p.site if p.site is not None else ''}"
        if isinstance(p, OpBin) and p.op == "*":
            return pauli_str(p.lhs) + pauli_str(p.rhs)
        raise AssertionError(f"unexpected Pauli-side node {p!r}")

    coeffs_ha: dict[str, float] = {}
    for term in flatten_sum(h_electronic):
        assert isinstance(term, OpBin) and term.op == "*", (
            f"expected a scalar*Pauli term, got {term!r}"
        )
        coeff_j = term.lhs.value
        key = pauli_str(term.rhs)
        coeffs_ha[key] = coeff_j / _HA_TO_J
    return coeffs_ha


def test_h_electronic_coefficients_match_literature() -> None:
    coeffs = _extract_h_electronic_coefficients()
    assert set(coeffs) == set(_EXPECTED_HA), (
        f"unexpected term set {sorted(coeffs)} vs expected {sorted(_EXPECTED_HA)}"
    )
    for key, expected in _EXPECTED_HA.items():
        actual = coeffs[key]
        assert abs(actual - expected) < _TOL_HA, (
            f"{key}: computed {actual:.4f} Ha, expected {expected} Ha "
            f"(research note / O'Malley et al. 2016 Table 1)"
        )


def test_full_identity_coefficient_matches_literature_once_nuclear_repulsion_is_added() -> (
    None
):
    coeffs = _extract_h_electronic_coefficients()
    g0_full = coeffs["I"] + _E_NN_HA
    assert abs(g0_full - _LITERATURE_FULL_G0_HA) < _TOL_HA, (
        f"g0_electronic + E_nn = {g0_full:.4f} Ha, expected "
        f"{_LITERATURE_FULL_G0_HA} Ha (literature's full g0)"
    )
