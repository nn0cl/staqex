"""SV-21: capply(ctrl, U, tgt) — controlled unitaries (ADR 0043)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure, as_main, assertNormEquals, assertSuperposition
from harness.report import CaseResult
from harness.state import State

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def _eval(src: str, seed: int = 0):
    compiled = compile_source(src)
    if compiled.unit is None:
        raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
    hard = [
        d
        for d in compiled.diagnostics
        if d.get("code")
        in {
            "PARSE_ERROR",
            "LEX_ERROR",
            "TOPLEVEL_EXECUTION_ERROR",
            "DIMENSION_MISMATCH_ERROR",
            "TYPE_NOT_STATE",
        }
    ]
    if hard:
        raise AssertionFailure(hard[0]["code"], str(hard))
    return Evaluator(seed=seed).run_unit(compiled.unit, stdout=io.StringIO()), compiled


def _norm(joint) -> float:
    return sum(abs(w.amp) ** 2 for w in joint.worlds)


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # capply(X) ≡ cnot → Φ⁺
    try:
        result, _ = _eval(
            as_main(
                """
State a = |+>
State b = |0>
State b = capply(a, X, b)
State zz = expect(ZZ, a, b)
Measure zz
"""
            )
        )
        if abs(_norm(result.joint) - 1.0) > 1e-9:
            raise AssertionFailure("NORM", f"norm={_norm(result.joint)}")
        marg = result.joint.marginal("zz")
        val = next(iter(marg.keys()))
        if abs(float(val) - 1.0) > 1e-9:
            raise AssertionFailure("CORR", f"⟨ZZ⟩={val}")
        # support |00>+|11|
        st_a = State(
            {
                0: sum(abs(w.amp) ** 2 for w in result.joint.worlds if w.assign.get("a") == 0),
                1: sum(abs(w.amp) ** 2 for w in result.joint.worlds if w.assign.get("a") == 1),
            },
            payload_type=int,
        )
        assertNormEquals(st_a, 1.0)
        out.append(
            CaseResult(
                "SV-21",
                "sv21-capply-x-bell",
                "capply(X) prep Φ⁺ with ⟨ZZ⟩=+1",
                True,
                ["capply", "X"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-21",
                "sv21-capply-x-bell",
                "capply(X) prep Φ⁺ with ⟨ZZ⟩=+1",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # cnot vs capply(X) same Born on target
    try:
        r1, _ = _eval(
            as_main(
                """
State a = |+>
State b = |0>
State b = cnot(a, b)
Measure b
"""
            )
        )
        r2, _ = _eval(
            as_main(
                """
State a = |+>
State b = |0>
State b = capply(a, X, b)
Measure b
"""
            )
        )
        m1 = r1.joint.marginal("b")
        m2 = r2.joint.marginal("b")
        for k in set(m1) | set(m2):
            if abs(m1.get(k, 0) - m2.get(k, 0)) > 1e-9:
                raise AssertionFailure("MISMATCH", f"cnot≠capply X: {m1} vs {m2}")
        out.append(
            CaseResult(
                "SV-21",
                "sv21-cnot-equiv-capply-x",
                "cnot ≡ capply(_, X, _) on Φ⁺ prep",
                True,
                ["cnot", "capply"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-21",
                "sv21-cnot-equiv-capply-x",
                "cnot ≡ capply(_, X, _) on Φ⁺ prep",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # CZ on |11⟩ flips relative phase; |01⟩ untouched populations
    try:
        result, _ = _eval(
            as_main(
                """
State a = |1>
State b = |1>
State b = capply(a, Z, b)
State ez = expect(Z, b)
Measure ez
"""
            )
        )
        # |11⟩ → -|11⟩; ⟨Z⟩ on b still −1
        marg = result.joint.marginal("ez")
        val = next(iter(marg.keys()))
        if abs(float(val) - (-1.0)) > 1e-9:
            raise AssertionFailure("PHASE", f"⟨Z⟩={val} after CZ on |11⟩")
        # amplitude should be negative real (phase -1)
        amps = [
            w.amp
            for w in result.joint.worlds
            if w.assign.get("a") == 1 and w.assign.get("b") == 1
        ]
        if not amps or abs(amps[0] + 1.0) > 1e-9:
            raise AssertionFailure("PHASE", f"amp={amps} expected −1")
        out.append(
            CaseResult(
                "SV-21",
                "sv21-capply-z-phase",
                "capply(Z) on |11⟩ → phase −1, ⟨Z⟩=−1",
                True,
                ["CZ"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-21",
                "sv21-capply-z-phase",
                "capply(Z) on |11⟩ → phase −1, ⟨Z⟩=−1",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # ctrl=0 → identity
    try:
        result, _ = _eval(
            as_main(
                """
State a = |0>
State b = |0>
State b = capply(a, X, b)
Measure b
"""
            )
        )
        st = State(result.joint.marginal("b"), payload_type=int)
        assertSuperposition(st, {0: 1.0})
        out.append(
            CaseResult(
                "SV-21",
                "sv21-capply-ctrl0-id",
                "capply with ctrl=0 leaves target",
                True,
                ["controlled-I"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-21",
                "sv21-capply-ctrl0-id",
                "capply with ctrl=0 leaves target",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # Example file
    try:
        src = (_REPO / "examples/applied/A01_quantum_attention_toy/main_quantum_attention_toy.sqx").read_text(
            encoding="utf-8"
        )
        result, _ = _eval(src)
        if result.measure is None:
            raise AssertionFailure("MEASURE", "no Measure")
        out.append(
            CaseResult(
                "SV-21",
                "sv21-example-file",
                "controlled_unitary.sqx runs",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-21",
                "sv21-example-file",
                "controlled_unitary.sqx runs",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
