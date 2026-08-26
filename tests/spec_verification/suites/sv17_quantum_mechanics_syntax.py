"""SV-17: Dirac ket, Evolve under H, expect, pretty dimension errors (ADR 0038)."""

from __future__ import annotations

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
    ev = Evaluator(seed=seed)
    return ev.run_unit(compiled.unit, stdout=io.StringIO()), compiled


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Ket |0> / |+>
    try:
        src = as_main(
            """
State z = |0>
State p = |+>
Measure z
"""
        )
        result, _ = _eval(src)
        st = State(result.joint.marginal("z"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0: 1.0})
        # |+> born masses
        result2, _ = _eval(
            as_main(
                """
State p = |+>
Measure p
"""
            )
        )
        st2 = State(result2.joint.marginal("p"), payload_type=int)
        assertNormEquals(st2, 1.0)
        assertSuperposition(st2, {0: 0.5, 1: 0.5})
        out.append(
            CaseResult(
                "SV-17",
                "sv17-ket-literals",
                "|0> Dirac; |+> equal superposition",
                True,
                ["KetLit"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-17",
                "sv17-ket-literals",
                "ket literals",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # evolve under Z for π: |+> → phase → ⟨Z⟩ = 0 still? 
    # e^{-i Z π} |+> = (e^{-iπ}|0> + e^{iπ}|1>)/√2 = (-|0> - |1>)/√2 = -|+>
    # global phase; ⟨Z⟩ still 0. Better: |0> under Z for π → e^{-iπ}|0> = -|0>, ⟨Z⟩=1
    # |+> under X for π/2: ...
    # Test: |0> under X for π → |1>  (e^{-i X π} = -i X, up to global phase maps 0→1)
    # cos(π)=-1, sin(π)=0 → U = -I, stays |0>. 
    # For X: U(π/2) = cos(π/2)I - i sin(π/2)X = -i X → |0> → -i|1>
    try:
        # LISS-0337: the bare single-Pauli-letter evolve form (`under X
        # for t`) routes through quantum_ops.pauli_u, which is NOT
        # hbar-divided (ADR 0195 only changed the Operator-declared H
        # paths) -- `t` remains a raw rotation angle. Declaring it in
        # `.s` (canonical seconds, scale 1.0) passes the exact pi/2
        # value through the fail-closed Time-unit check unchanged.
        src = as_main(
            """
State psi0 = |0>
Time dur = 1.5707963267948966.s
State psi = Evolve { psi0 under X for dur }.run()
Measure psi
"""
        )
        result, _ = _eval(src)
        marg = result.joint.marginal("psi")
        # Should be essentially |1>
        if 1 not in marg or marg[1] < 0.99:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"marg={marg}")
        out.append(
            CaseResult(
                "SV-17",
                "sv17-Evolve-under-x",
                "Evolve |0> under X for π/2 → |1>",
                True,
                ["hamiltonian"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-17",
                "sv17-Evolve-under-x",
                "Evolve under X",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # expect(Z, |0>) = 1; expect(Z, |+>) = 0
    try:
        src = as_main(
            """
State z = |0>
State ez = expect(Z, z)
Measure ez
"""
        )
        result, _ = _eval(src)
        marg = result.joint.marginal("ez")
        st = State({round(k, 10): v for k, v in marg.items()}, payload_type=float)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {1.0: 1.0})

        src2 = as_main(
            """
State p = |+>
State ez = expect(Z, p)
Measure ez
"""
        )
        result2, _ = _eval(src2)
        marg2 = result2.joint.marginal("ez")
        keys = list(marg2.keys())
        if len(keys) != 1 or abs(float(keys[0])) > 1e-9:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"⟨Z⟩_+ = {marg2}")
        out.append(
            CaseResult(
                "SV-17",
                "sv17-expect-z",
                "expect(Z,|0>)=1; expect(Z,|+>)=0",
                True,
                ["expect"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-17",
                "sv17-expect-z",
                "expect Z",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Φ⁺ via |+>⊗|0> + CNOT; ⟨Z⊗Z⟩ = +1 (no nested when)
    try:
        src = as_main(
            """
State alice = |+>
State bob = |0>
State bob = cnot(alice, bob)
State corr = expect(ZZ, alice, bob)
Measure corr
"""
        )
        result, _ = _eval(src)
        # Entangled support: only (0,0) and (1,1)
        # After measure(corr), check corr marginal; also verify joint before measure
        # via expect already bound — re-eval without measure to inspect pair
        src2 = as_main(
            """
State alice = |+>
State bob = |0>
State bob = cnot(alice, bob)
State corr = expect(ZZ, alice, bob)
Snapshot corr to sink
Measure corr
"""
        )
        result2, _ = _eval(src2)
        # alice/bob still present (expect non-destructive)
        for w in result2.joint.worlds:
            a, b = w.assign.get("alice"), w.assign.get("bob")
            if a is None or b is None:
                continue
            if a != b:
                raise AssertionFailure(
                    "SUPERPOSITION_MISMATCH",
                    f"Φ+ support broken: world {w.assign}",
                )
        marg = result.joint.marginal("corr")
        keys = list(marg.keys())
        if len(keys) != 1 or abs(float(keys[0]) - 1.0) > 1e-9:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"⟨ZZ⟩={marg}")
        out.append(
            CaseResult(
                "SV-17",
                "sv17-cnot-zz",
                "cnot prep Φ+; expect(ZZ)=+1",
                True,
                ["cnot", "ZZ"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-17",
                "sv17-cnot-zz",
                "cnot ZZ",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Pretty dimension error: [Length] vs [Time]
    try:
        src = as_main(
            """
State<Length> x = Dirac(1.0.m)
Delta<Time> dt = 0.5.s
State bad = x + dt
Measure bad
"""
        )
        compiled = compile_source(src)
        dims = [d for d in compiled.diagnostics if d.get("code") == "DIMENSION_MISMATCH_ERROR"]
        if not dims:
            raise AssertionFailure("DIMENSION_MISMATCH_ERROR", "missing dim error")
        msg = dims[0].get("message", "")
        if "[Length]" not in msg or "[Time]" not in msg:
            raise AssertionFailure(
                "DIMENSION_MISMATCH_ERROR",
                f"expected pretty names in message, got {msg!r}",
            )
        out.append(
            CaseResult(
                "SV-17",
                "sv17-dim-pretty",
                "dim error uses [Length] vs [Time]",
                True,
                ["DIMENSION_MISMATCH_ERROR"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-17",
                "sv17-dim-pretty",
                "pretty dims",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
