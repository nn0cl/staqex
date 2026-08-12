"""SV-29: Position-grid HO — X/P + wavepacket (ADR 0051)."""

from __future__ import annotations

import io
import math
import sys
from pathlib import Path

from harness import AssertionFailure, as_main
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.hamiltonian import compile_hamiltonian, op_n_qubits  # noqa: E402
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


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    try:
        src = as_main(
            """
state psi = wavepacket(-6.0, 6.0, 32, 0.0, 0.7071067811865476)
Operator H = 0.5 * (P * P + X * X)
measure psi
"""
        )
        compiled = compile_source(src)
        ops = {
            st.names[0]: st.expr
            for st in compiled.unit.main.body.stmts
            if getattr(st, "ty", None) and st.ty and st.ty.name == "Operator"
        }
        if op_n_qubits(ops["H"], ops, {}) != -1:
            raise AssertionFailure("MODE", "expected grid mode")
        xs = [-6.0 + i * (12.0 / 32) for i in range(32)]
        h = compile_hamiltonian(ops["H"], env=ops, n_qubits=-1, grid_xs=xs)
        herm = frobenius_norm(mat_add(h, mat_scale(mat_dag(h), -1)))
        if herm > 1e-9:
            raise AssertionFailure("HERMITIAN", f"||H-H†||={herm}")
        out.append(
            CaseResult(
                "SV-29",
                "sv29-grid-hermitian",
                "H=½(P²+X²) Hermitian on position grid",
                True,
                ["X", "P"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-29",
                "sv29-grid-hermitian",
                "H=½(P²+X²) Hermitian on position grid",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    try:
        result, _ = _eval(
            as_main(
                """
state psi = wavepacket(-6.0, 6.0, 48, 0.0, 0.7071067811865476)
Energy e = 0.5.eV to J
Time dur = 1.0.fs
Operator H = e * (P * P + X * X)
state psi = evolve { psi under H for dur }.run()
measure psi
"""
            )
        )
        n = sum(abs(w.amp) ** 2 for w in result.joint.worlds)
        if abs(n - 1.0) > 1e-8:
            raise AssertionFailure("NORM", f"norm={n}")
        marg = result.joint.marginal("psi")
        mean = sum(float(k) * p for k, p in marg.items())
        if abs(mean) > 0.15:
            raise AssertionFailure("MEAN", f"⟨x⟩={mean}")
        out.append(
            CaseResult(
                "SV-29",
                "sv29-evolve-norm-mean",
                "grid evolve preserves norm; ⟨x⟩≈0 for centered Gaussian",
                True,
                ["wavepacket"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-29",
                "sv29-evolve-norm-mean",
                "grid evolve preserves norm; ⟨x⟩≈0 for centered Gaussian",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    try:
        src = (
            _REPO / "tests/fixtures/staqex/grid_oscillator.sqx"
        ).read_text(encoding="utf-8")
        result, _ = _eval(src)
        if result.measure is None:
            raise AssertionFailure("MEASURE", "no measure")
        out.append(
            CaseResult(
                "SV-29",
                "sv29-example",
                "grid_oscillator.sqx runs",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-29",
                "sv29-example",
                "grid_oscillator.sqx runs",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
