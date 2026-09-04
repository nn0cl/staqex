"""SV-20: apply(U,…), hadamard, shift — true DTQW surface (ADR 0042)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure, as_main, assertNormEquals, assertSuperposition
from harness.report import CaseResult
from harness.state import State
from harness.canonical_execution import run_canonical

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
    return run_canonical(compiled, ev, stdout=io.StringIO()), compiled


def _norm(joint) -> float:
    return sum(abs(w.amp) ** 2 for w in joint.worlds)


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # hadamard(|0>) = |+>
    try:
        result, _ = _eval(
            as_main(
                """
State c = |0>
State c = hadamard(c)
Measure c
"""
            )
        )
        st = State(result.joint.marginal("c"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0: 0.5, 1: 0.5})
        out.append(
            CaseResult(
                "SV-20",
                "sv20-hadamard",
                "hadamard(|0>) → |+>",
                True,
                ["hadamard"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-20",
                "sv20-hadamard",
                "hadamard(|0>) → |+>",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # apply(X, |0>) → |1>
    try:
        result, _ = _eval(
            as_main(
                """
State c = |0>
State c = apply(X, c)
Measure c
"""
            )
        )
        st = State(result.joint.marginal("c"), payload_type=int)
        assertSuperposition(st, {1: 1.0})
        out.append(
            CaseResult(
                "SV-20",
                "sv20-apply-x",
                "apply(X,|0>) → |1>",
                True,
                ["apply"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-20",
                "sv20-apply-x",
                "apply(X,|0>) → |1>",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # apply Operator Hadamard-like on joint (H⊗I) + shift
    try:
        result, _ = _eval(
            as_main(
                """
Operator CoinOp = 0.7071067811865476 * (X + Z)
State c = |0>
State x = Dirac(0)
State (c, x) = c *|* x
State c = apply(CoinOp, c)
State x = walk_shift(c, x)
Measure x
"""
            )
        )
        if abs(_norm(result.joint) - 1.0) > 1e-9:
            raise AssertionFailure("NORM", f"norm={_norm(result.joint)}")
        st = State(result.joint.marginal("x"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {-1: 0.5, 1: 0.5})
        out.append(
            CaseResult(
                "SV-20",
                "sv20-dtqw-one-step",
                "apply(Coin)∘shift: |0⟩|0⟩ → equal mass on ±1",
                True,
                ["apply", "shift", "*|*"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-20",
                "sv20-dtqw-one-step",
                "apply(Coin)∘shift: |0⟩|0⟩ → equal mass on ±1",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # Two-step DTQW position masses {-2:1/4, 0:1/2, 2:1/4}
    try:
        result, _ = _eval(
            as_main(
                """
Operator CoinOp = 0.7071067811865476 * (X + Z)
State c = |0>
State x = Dirac(0)
State (c, x) = c *|* x
State c = apply(CoinOp, c)
State x = walk_shift(c, x)
State c = apply(CoinOp, c)
State x = walk_shift(c, x)
Measure x
"""
            )
        )
        st = State(result.joint.marginal("x"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {-2: 0.25, 0: 0.5, 2: 0.25})
        out.append(
            CaseResult(
                "SV-20",
                "sv20-dtqw-two-step",
                "2-step DTQW position {-2:¼, 0:½, 2:¼}",
                True,
                ["DTQW"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-20",
                "sv20-dtqw-two-step",
                "2-step DTQW position {-2:¼, 0:½, 2:¼}",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # apply(Hadamard, …) named gate
    try:
        result, _ = _eval(
            as_main(
                """
State c = |0>
State c = apply(Hadamard, c)
Measure c
"""
            )
        )
        st = State(result.joint.marginal("c"), payload_type=int)
        assertSuperposition(st, {0: 0.5, 1: 0.5})
        out.append(
            CaseResult(
                "SV-20",
                "sv20-apply-hadamard-name",
                "apply(Hadamard,|0>) → |+>",
                True,
                ["Hadamard"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-20",
                "sv20-apply-hadamard-name",
                "apply(Hadamard,|0>) → |+>",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # Example files
    try:
        for rel in (
            "tests/fixtures/staqex/dtqw.sqx",
            "tests/fixtures/staqex/classical_walk.sqx",
            "tests/fixtures/staqex/quantum_vs_classical_walk.sqx",
        ):
            src = (_REPO / rel).read_text(encoding="utf-8")
            result, _ = _eval(src)
            if result.measure is None:
                raise AssertionFailure("MEASURE", f"no Measure in {rel}")
        out.append(
            CaseResult(
                "SV-20",
                "sv20-example-files",
                "dtqw + classical_walk + interfer pedagogy run",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-20",
                "sv20-example-files",
                "dtqw + classical_walk + interfer pedagogy run",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
