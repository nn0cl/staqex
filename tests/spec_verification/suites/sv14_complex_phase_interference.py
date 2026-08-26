"""SV-14: Complex amplitudes — phase, cis, destructive interfer → Vacuum."""

from __future__ import annotations

import cmath
import io
import math
import sys
from pathlib import Path

from harness import AssertionFailure, as_main, assertNormEquals, assertSuperposition
from harness.report import CaseResult
from harness.state import State

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_path, compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.joint import cis  # noqa: E402


def _eval(src: str, seed: int = 0):
    compiled = compile_source(src)
    if compiled.unit is None:
        raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
    hard = [
        d
        for d in compiled.diagnostics
        if d.get("code") in {"FORBIDDEN_KEYWORD", "EARLY_COLLAPSE_ERROR", "PARSE_ERROR"}
    ]
    if hard:
        raise AssertionFailure(hard[0]["code"], str(hard))
    ev = Evaluator(seed=seed)
    return ev.run_unit(compiled.unit, stdout=io.StringIO())


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Opposite phases cancel completely under interfer
    try:
        src = as_main("""
State z = Dirac(0)
State zp = phase(z, pi)
State out = interfer(z, zp)
Measure out
""")
        result = _eval(src)
        if not result.joint.is_vacuum():
            raise AssertionFailure(
                "SUPERPOSITION_MISMATCH",
                f"expected Vacuum after cancel, joint={result.joint.support_rows()}",
            )
        if result.measure is None or not result.measure.vacuum:
            raise AssertionFailure(
                "SUPERPOSITION_MISMATCH",
                f"Measure should report Vacuum, got {result.measure}",
            )
        out.append(
            CaseResult(
                "SV-14",
                "sv14-destructive-Vacuum",
                "e^{i0} + e^{iπ} → interfer → Vacuum",
                True,
                ["assertVacuum"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-14",
                "sv14-destructive-Vacuum",
                "destructive interfer → Vacuum",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Same phase constructively reinforces (renormalized Dirac)
    try:
        src = as_main("""
State a = Dirac(7)
State b = phase(a, 0.0)
State out = interfer(a, b)
Measure out
""")
        result = _eval(src)
        st = State(result.joint.marginal("out"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {7: 1.0})
        out.append(
            CaseResult(
                "SV-14",
                "sv14-constructive-Dirac",
                "same-phase interfer → Dirac(7)",
                True,
                ["assertSuperposition", "assertNormEquals"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-14",
                "sv14-constructive-Dirac",
                "constructive interfer",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # cis(θ) matches e^{iθ}; Complex.cis available
    try:
        if abs(cis(math.pi) - (-1 + 0j)) > 1e-9:
            raise AssertionFailure("NORM_MISMATCH", f"cis(π)={cis(math.pi)}")
        src = as_main("""
State u = Complex.cis(pi)
Measure u
""")
        result = _eval(src)
        rows = result.joint.support_rows()
        if len(rows) != 1 or rows[0]["assignment"].get("u") != 0:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"rows={rows}")
        amp = rows[0]["amp"]
        if abs(amp - cmath.exp(1j * math.pi)) > 1e-9:
            raise AssertionFailure("NORM_MISMATCH", f"amp={amp}")
        out.append(
            CaseResult(
                "SV-14",
                "sv14-cis-prelude",
                "cis / Complex.cis(π) = −1 on |0⟩",
                True,
                ["cis", "Complex.cis"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-14",
                "sv14-cis-prelude",
                "cis prelude",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Double-slit: shared bin cancelled
    try:
        src = (_REPO / "examples/basics/B05_phase_interference/phase_interference.sqx").read_text(
            encoding="utf-8"
        )
        result = _eval(src)
        marg = result.joint.marginal("screen")
        if 1 in marg:
            raise AssertionFailure(
                "SUPERPOSITION_MISMATCH",
                f"bin 1 should cancel, marg={marg}",
            )
        st = State(marg, payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0: 0.5, 2: 0.5})
        out.append(
            CaseResult(
                "SV-14",
                "sv14-double-slit-cancel",
                "double_slit: bin 1 destructive cancel",
                True,
                ["assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-14",
                "sv14-double-slit-cancel",
                "double_slit cancel",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Grover: oracle phase + diffuse → target
    try:
        path = _REPO / "examples/applied/A04_hp_protein_folding/main_hp_protein_folding.sqx"
        compiled = compile_path(path)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        ev = Evaluator(seed=0)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        marg = result.joint.marginal("amplified")
        st = State(marg, payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {1: 1.0})
        out.append(
            CaseResult(
                "SV-14",
                "sv14-grover-amplify",
                "grover phase+diffuse → |1⟩",
                True,
                ["assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-14",
                "sv14-grover-amplify",
                "grover amplify",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
