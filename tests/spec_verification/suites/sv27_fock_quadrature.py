"""SV-27: Fock Q/P quadratures — H = ½(P²+Q²) (ADR 0049)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure, as_main
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.hamiltonian import compile_hamiltonian  # noqa: E402
from compiler.staqex.runtime.matrix import (  # noqa: E402
    frobenius_norm,
    mat_add,
    mat_dag,
    mat_scale,
)


def _eval(src: str, seed: int = 0):
    compiled = compile_source(src)
    if compiled.unit is None:
        raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
    hard = [d for d in compiled.diagnostics if d.get("code") in {"PARSE_ERROR", "LEX_ERROR"}]
    if hard:
        raise AssertionFailure(hard[0]["code"], str(hard))
    return Evaluator(seed=seed).run_unit(compiled.unit, stdout=io.StringIO()), compiled


def _ops_from(src: str) -> dict:
    compiled = compile_source(src)
    if compiled.unit is None or compiled.unit.main is None:
        raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
    ops = {}
    for st in compiled.unit.main.body.stmts:
        ty = getattr(st, "ty", None)
        if ty is not None and ty.name == "Operator":
            ops[st.names[0]] = st.expr
    return ops


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    try:
        ops = _ops_from(
            as_main(
                """
Operator Hxp = 0.5 * (P * P + Q * Q)
State x = dirac(0)
measure x
"""
            )
        )
        h = compile_hamiltonian(ops["Hxp"], env=ops, n_qubits=0, fock_dim=8)
        herm = frobenius_norm(mat_add(h, mat_scale(mat_dag(h), -1)))
        if herm > 1e-9:
            raise AssertionFailure("HERMITIAN", f"||H-H†||={herm}")
        e0 = h[0][0].real
        if abs(e0 - 0.5) > 1e-9:
            raise AssertionFailure("E0", f"E0={e0}")
        out.append(
            CaseResult(
                "SV-27",
                "sv27-hermitian-e0",
                "H=½(P²+Q²) Hermitian with E₀=½",
                True,
                ["Q", "P"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-27",
                "sv27-hermitian-e0",
                "H=½(P²+Q²) Hermitian with E₀=½",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    try:
        # LISS-0337: Time-typed duration to satisfy ADR 0195's fail-closed
        # check. dirac(0) is an eigenstate of H=0.5(P^2+Q^2), so the
        # assertion (population stays at |0>) is invariant to the exact
        # real duration chosen.
        result, _ = _eval(
            as_main(
                """
Energy e = 0.5.eV to J
Time dur = 1.0.fs
Operator H = e * (P * P + Q * Q)
State psi = dirac(0)
State psi = evolve { psi under H for dur }.run()
measure psi
"""
            )
        )
        m = result.joint.marginal("psi")
        if abs(m.get(0, 0.0) - 1.0) > 1e-8:
            raise AssertionFailure("NORM", str(m))
        out.append(
            CaseResult(
                "SV-27",
                "sv27-evolve-ground",
                "evolve |0⟩ under H_xp stays |0⟩",
                True,
                ["evolve"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-27",
                "sv27-evolve-ground",
                "evolve |0⟩ under H_xp stays |0⟩",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    try:
        src = (_REPO / "tests/fixtures/staqex/xp_oscillator.sqx").read_text(
            encoding="utf-8"
        )
        result, _ = _eval(src)
        if result.measure is None:
            raise AssertionFailure("MEASURE", "no measure")
        out.append(
            CaseResult(
                "SV-27",
                "sv27-example",
                "xp_oscillator.sqx runs",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-27",
                "sv27-example",
                "xp_oscillator.sqx runs",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
