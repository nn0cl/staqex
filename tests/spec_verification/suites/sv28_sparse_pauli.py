"""SV-28: Sparse Pauli-sum IR for multi-qubit Evolve (ADR 0050)."""

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

from compiler.staqex.ast_nodes import LitFloat  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.hamiltonian import compile_hamiltonian  # noqa: E402
from compiler.staqex.runtime.matrix import (  # noqa: E402
    apply_mat,
    expm_ih,
    frobenius_norm,
    mat_add,
    mat_scale,
)
from compiler.staqex.runtime.sparse_pauli import (  # noqa: E402
    compile_sparse_pauli,
    expm_ih_apply,
    sparse_to_dense,
)


def _eval(src: str, seed: int = 0):
    compiled = compile_source(src)
    if compiled.unit is None:
        raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
    hard = [d for d in compiled.diagnostics if d.get("code") in {"PARSE_ERROR", "LEX_ERROR"}]
    if hard:
        raise AssertionFailure(hard[0]["code"], str(hard))
    return Evaluator(seed=seed).run_unit(compiled.unit, stdout=io.StringIO()), compiled


def _ops_scalars(compiled):
    ops = {}
    scalars = {}
    for st in compiled.unit.main.body.stmts:
        ty = getattr(st, "ty", None)
        if ty is None:
            continue
        if ty.name == "Operator":
            ops[st.names[0]] = st.expr
        elif ty.name == "Float" and isinstance(st.expr, LitFloat):
            scalars[st.names[0]] = st.expr.value
    return ops, scalars


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # sparse H ≡ dense H
    try:
        src = as_main(
            """
Float J = 1.0
Float h = 0.5
Operator H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
State a = |0>
Measure a
"""
        )
        compiled = compile_source(src)
        ops, scalars = _ops_scalars(compiled)
        hd = compile_hamiltonian(ops["H"], env=ops, scalars=scalars, n_qubits=2)
        sp = compile_sparse_pauli(ops["H"], env=ops, scalars=scalars, n_qubits=2)
        hs = sparse_to_dense(sp)
        err = frobenius_norm(mat_add(hd, mat_scale(hs, -1)))
        if err > 1e-12:
            raise AssertionFailure("SPARSE_H", f"||H_d-H_s||={err}")
        out.append(
            CaseResult(
                "SV-28",
                "sv28-sparse-eq-dense-h",
                "sparse Pauli sum ≡ dense Ising H",
                True,
                ["sparse"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-28",
                "sv28-sparse-eq-dense-h",
                "sparse Pauli sum ≡ dense Ising H",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # Taylor e^{-iHt}|ψ⟩ ≡ dense U|ψ⟩
    try:
        src = as_main(
            """
Float J = 1.0
Float h = 0.25
Operator H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
State a = |0>
Measure a
"""
        )
        compiled = compile_source(src)
        ops, scalars = _ops_scalars(compiled)
        hd = compile_hamiltonian(ops["H"], env=ops, scalars=scalars, n_qubits=2)
        sp = compile_sparse_pauli(ops["H"], env=ops, scalars=scalars, n_qubits=2)
        vec = [math.sqrt(0.5), 0j, math.sqrt(0.5), 0j]
        # LISS-0337: expm_ih/expm_ih_apply now divide by real hbar (ADR
        # 0195); J/h here are bare (dimensionless, magnitude ~1) scalars,
        # not real Joule-scale values, so t must be picked on hbar's own
        # scale to keep |H*t/hbar| a moderate O(1) phase (both sides use
        # the same t, so the sparse == dense equivalence is unaffected
        # by the absolute scale chosen).
        from compiler.staqex.stdlib.prelude import HBAR_SI

        t = HBAR_SI
        vd = apply_mat(expm_ih(hd, t), vec)
        vs = expm_ih_apply(sp, t, vec)
        err = sum(abs(a - b) ** 2 for a, b in zip(vd, vs)) ** 0.5
        if err > 1e-10:
            raise AssertionFailure("TAYLOR", f"state err {err}")
        out.append(
            CaseResult(
                "SV-28",
                "sv28-taylor-eq-dense-u",
                "sparse Taylor e^{-iHt} ≡ dense U",
                True,
                ["expm"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-28",
                "sv28-taylor-eq-dense-u",
                "sparse Taylor e^{-iHt} ≡ dense U",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # 4-qubit evolve preserves norm
    try:
        result, _ = _eval(
            as_main(
                """
Energy J = 1.0.eV to J
Time dur = 1.0.fs
Operator H = -J * (Z[0]*Z[1] + Z[1]*Z[2] + Z[2]*Z[3] + Z[3]*Z[0])
State q0 = |+>
State q1 = |0>
State q2 = |0>
State q3 = |0>
State (q0, q1, q2, q3) = Evolve { (q0, q1, q2, q3) under H for dur }.run()
Measure q0
"""
            )
        )
        n = sum(abs(w.amp) ** 2 for w in result.joint.worlds)
        if abs(n - 1.0) > 1e-8:
            raise AssertionFailure("NORM", f"norm={n}")
        out.append(
            CaseResult(
                "SV-28",
                "sv28-ising4-norm",
                "4-qubit sparse Evolve preserves Born norm",
                True,
                ["n=4"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-28",
                "sv28-ising4-norm",
                "4-qubit sparse Evolve preserves Born norm",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    try:
        src = (
            _REPO / "tests/fixtures/staqex/quantum_ising_4.sqx"
        ).read_text(encoding="utf-8")
        result, _ = _eval(src)
        if result.measure is None:
            raise AssertionFailure("MEASURE", "no Measure")
        out.append(
            CaseResult(
                "SV-28",
                "sv28-example",
                "quantum_ising_4.sqx runs",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-28",
                "sv28-example",
                "quantum_ising_4.sqx runs",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
