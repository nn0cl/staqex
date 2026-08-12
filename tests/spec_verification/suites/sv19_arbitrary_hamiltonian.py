"""SV-19: Arbitrary Operator H, e^{-iHt}, tensor *|*, partial trace."""

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

from compiler.staqex.ast_nodes import OpBin, OpPauli, Span  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.hamiltonian import compile_hamiltonian  # noqa: E402
from compiler.staqex.runtime.matrix import expm_ih, mat_dag, mat_mul  # noqa: E402


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


def _joint_norm(joint) -> float:
    return sum(abs(w.amp) ** 2 for w in joint.worlds)


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # --- Fock H = N + 1/2: unitary norm ---
    try:
        src = as_main(
            """
Energy e = 0.5.eV to J
Time dur = 1.0.fs
Operator H = e * (N + 0.5)
State psi = Dirac(0)
State psi = Evolve { psi under H for dur }.run()
Measure psi
"""
        )
        result, _ = _eval(src)
        n = _joint_norm(result.joint)
        if abs(n - 1.0) > 1e-9:
            raise AssertionFailure("NORM", f"Fock Evolve norm {n}")
        st = State(result.joint.marginal("psi"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0: 1.0})
        out.append(
            CaseResult(
                "SV-19",
                "sv19-fock-ho-unitary",
                "Fock H=N+1/2 Evolve preserves |0⟩ and unit norm",
                True,
                ["Operator", "expm"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-19",
                "sv19-fock-ho-unitary",
                "Fock H=N+1/2 Evolve preserves |0⟩ and unit norm",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # --- Multi-qubit Ising: unitarity of U ---
    try:
        src = as_main(
            """
Energy J = 1.0.eV to J
Energy h = 0.25.eV to J
Time dur = 1.0.fs
Operator H = -J * (Z[0] * Z[1]) - h * (X[0] + X[1])
State a = |+>
State b = |0>
State (a, b) = Evolve { (a, b) under H for dur }.run()
State zz = expect(ZZ, a, b)
Measure zz
"""
        )
        result, _ = _eval(src)
        n = _joint_norm(result.joint)
        if abs(n - 1.0) > 1e-8:
            raise AssertionFailure("NORM", f"Ising Evolve norm {n}")
        # Energy proxy: ⟨ZZ⟩ is classical; joint still unit
        out.append(
            CaseResult(
                "SV-19",
                "sv19-ising-unitary",
                "Ising Operator H Evolve preserves Born norm",
                True,
                ["Operator", "Z[index]", "Float coeff"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-19",
                "sv19-ising-unitary",
                "Ising Operator H Evolve preserves Born norm",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # --- Matrix U†U ≈ I for compiled H ---
    try:
        sp = Span(1, 1)
        # H = Z[0]*Z[1]
        h_ast = OpBin(
            "*",
            OpPauli("Z", 0, sp),
            OpPauli("Z", 1, sp),
            sp,
        )
        h = compile_hamiltonian(h_ast, env={}, scalars={}, n_qubits=2)
        # LISS-0337: expm_ih now divides by real hbar (ADR 0195); this
        # direct-Python call bypasses .sqx entirely and h carries a bare
        # unit (dimensionless, magnitude 1) Pauli-product matrix, not a
        # real Joule-scale value -- so t must be picked on hbar's own
        # scale to keep |H*t/hbar| a moderate O(1) phase. Unitarity
        # (U dag U = I) holds for any real, finite phase.
        from compiler.staqex.stdlib.prelude import HBAR_SI

        u = expm_ih(h, HBAR_SI)
        udag = mat_dag(u)
        i_approx = mat_mul(udag, u)
        err = 0.0
        for i in range(4):
            for j in range(4):
                target = 1.0 if i == j else 0.0
                err += abs(i_approx[i][j] - target) ** 2
        if err > 1e-16:
            raise AssertionFailure("UNITARY", f"U†U err {err}")
        out.append(
            CaseResult(
                "SV-19",
                "sv19-expm-unitary-matrix",
                "expm(-iHt) satisfies U†U ≈ I",
                True,
                ["matrix.expm_ih"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-19",
                "sv19-expm-unitary-matrix",
                "expm(-iHt) satisfies U†U ≈ I",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # --- Tensor *|* + trace_out ---
    try:
        src = as_main(
            """
State a = |+>
State b = |0>
State (c, x) = a *|* b
State _t = trace_out(c)
Measure x
"""
        )
        result, _ = _eval(src)
        st = State(result.joint.marginal("x"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0: 1.0})
        # also closed form tensor
        src2 = as_main(
            """
State (c, x) = |+> *|* Dirac(0)
Measure x
"""
        )
        result2, _ = _eval(src2)
        n2 = _joint_norm(result2.joint)
        if abs(n2 - 1.0) > 1e-9:
            raise AssertionFailure("NORM", f"tensor prep norm {n2}")
        out.append(
            CaseResult(
                "SV-19",
                "sv19-tensor-trace-out",
                "`*|*` product + trace_out yields |0⟩ on remainder",
                True,
                ["TensorExpr", "trace_out"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-19",
                "sv19-tensor-trace-out",
                "`*|*` product + trace_out yields |0⟩ on remainder",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # --- Energy: |0⟩ under H=Z is eigenstate (phase only) ---
    try:
        src = as_main(
            """
Energy e = 1.0.eV to J
Time dur = 1.0.fs
Operator H = e * Z
State psi = |0>
State psi = Evolve { psi under H for dur }.run()
State ez = expect(Z, psi)
Measure ez
"""
        )
        result, _ = _eval(src)
        # ⟨Z⟩ on |0⟩ = +1 before and after
        marg = result.joint.marginal("ez")
        val = next(iter(marg.keys()))
        if abs(float(val) - 1.0) > 1e-9:
            raise AssertionFailure("ENERGY", f"⟨Z⟩={val} expected 1")
        st = State(result.joint.marginal("psi"), payload_type=int)
        assertSuperposition(st, {0: 1.0})
        out.append(
            CaseResult(
                "SV-19",
                "sv19-energy-eigenstate",
                "|0⟩ under H=Z: populations fixed, ⟨Z⟩=1",
                True,
                ["expect", "Evolve under H"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-19",
                "sv19-energy-eigenstate",
                "|0⟩ under H=Z: populations fixed, ⟨Z⟩=1",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # --- Official example files compile+run ---
    # LISS-0337: B08_operators_hamiltonians is a WP-0095-tracked,
    # not-yet-migrated example (still bare-float evolve durations) --
    # expected to keep failing here with EVOLVE_UNRESOLVED_UNIT_ERROR
    # until its own WP-0095 work unit lands. Catch KernelError too so
    # that known, tracked failure reports as a graceful FAIL instead of
    # crashing this whole suite (masking every other case's result).
    try:
        from compiler.staqex.runtime.evaluator import KernelError

        for rel in (
            "tests/fixtures/staqex/quantum_oscillator.sqx",
            "examples/basics/B08_operators_hamiltonians/operators_hamiltonians.sqx",
        ):
            path = _REPO / rel
            src = path.read_text(encoding="utf-8")
            try:
                result, compiled = _eval(src)
            except KernelError as ke:
                raise AssertionFailure(
                    getattr(ke, "code", "KERNEL_ERROR"), f"{rel}: {ke}"
                ) from ke
            if result.measure is None:
                raise AssertionFailure("MEASURE", f"no Measure in {rel}")
        out.append(
            CaseResult(
                "SV-19",
                "sv19-example-files",
                "quantum_oscillator + quantum_ising examples run",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-19",
                "sv19-example-files",
                "quantum_oscillator + quantum_ising examples run",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
