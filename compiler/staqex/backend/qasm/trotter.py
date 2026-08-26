"""Suzuki S2/S4 Pauli product formula for `evolve … under H for t` → QASM gates
(LISS-0008 / ADR 0063; step policy per LISS-0017 / ADR 0084 / LISS-0142,
mandatory per LISS-0050 / ADR 0094).

Kernel evolve semantics stay exact (Taylor / dense). This module only approximates
for gate backends. No vendor SDKs.
"""

from __future__ import annotations

import math
from typing import Sequence

from ...ast_nodes import (
    Attr,
    BinOp,
    Expr,
    LitFloat,
    LitInt,
    OpExpr,
    Var,
    SuzukiPolicy,
)
from ...runtime.sparse_pauli import PauliTerm, SparsePauli, compile_sparse_pauli
from .circuit import Gate

# Reject codes (surfaced via Circuit.reject_code / EmitResult)
REJECT_UNSUPPORTED_H = "QASM_TROTTER_UNSUPPORTED_H"
REJECT_BAD_TIME = "QASM_TROTTER_BAD_TIME"
REJECT_COMPLEX_COEFF = "QASM_TROTTER_COMPLEX_COEFF"

_MIN_STEPS = 1


class TrotterError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def eval_time_expr(expr: Expr | int | float, scalars: dict[str, float]) -> float:
    """Evaluate `for t` classical duration (literals / prelude / simple arith)."""
    if isinstance(expr, (int, float)) and not isinstance(expr, bool):
        return float(expr)
    v = _eval_float(expr, scalars)  # type: ignore[arg-type]
    if v is None:
        raise TrotterError(REJECT_BAD_TIME, "evolve duration is not a closed classical float")
    return v


def compile_hamiltonian(
    hop: object,
    *,
    env: dict[str, OpExpr],
    scalars: dict[str, float],
    n_qubits: int,
) -> SparsePauli:
    """Resolve Operator AST / name → sparse Pauli; reject Fock / non-Pauli."""
    from ...ast_nodes import (
        OpBin,
        OpHop,
        OpIndexed,
        OpLit,
        OpNumber,
        OpPauli,
        OpPow,
        OpQuadrature,
        OpVar,
    )

    _OP = (OpBin, OpHop, OpIndexed, OpLit, OpNumber, OpPauli, OpPow, OpQuadrature, OpVar)
    if isinstance(hop, Var):
        if hop.name not in env:
            raise TrotterError(REJECT_UNSUPPORTED_H, f"unknown Operator `{hop.name}`")
        op: OpExpr = env[hop.name]
    elif isinstance(hop, _OP):
        op = hop  # type: ignore[assignment]
    else:
        raise TrotterError(
            REJECT_UNSUPPORTED_H,
            f"hamiltonian must be Operator name or Pauli AST, got {type(hop).__name__}",
        )
    try:
        return compile_sparse_pauli(op, env=env, scalars=scalars, n_qubits=n_qubits)
    except ValueError as e:
        raise TrotterError(REJECT_UNSUPPORTED_H, str(e)) from e


def suzuki_step_count(
    terms: Sequence[PauliTerm],
    t: float,
    *,
    tolerance: float | None = None,
    error_mode: str | None = None,
    steps: int | None = None,
    order: int = 2,
) -> int:
    """Resolve the statically fixed step count for S2/S4 (ADR 0084).

    Direct ``steps`` is preserved exactly.  Tolerance mode uses the ADR 0084
    alpha bound/estimate and never silently clamps the resulting value.
    """
    if steps is not None and tolerance is not None:
        raise TrotterError("SUZUKI_POLICY_ERROR", "steps and tolerance are mutually exclusive")
    if steps is not None:
        if int(steps) < 1:
            raise TrotterError("SUZUKI_POLICY_ERROR", "steps must be positive")
        return int(steps)
    if tolerance is None or error_mode not in {"Bound", "EmpiricalEstimate"}:
        raise TrotterError(
            "SUZUKI_POLICY_ERROR",
            "tolerance mode requires error = Bound or EmpiricalEstimate",
        )
    epsilon = float(tolerance)
    if epsilon <= 0.0:
        raise TrotterError("SUZUKI_POLICY_ERROR", "tolerance must be positive")
    if order not in {2, 4}:
        raise TrotterError("SUZUKI_ORDER_ERROR", "Suzuki supports order 2 or 4")
    alpha = sum(abs(term.coeff) for term in terms)
    abs_t = abs(float(t))
    if order == 2:
        denominator = 12.0 if error_mode == "Bound" else 120.0
        estimate = math.sqrt((alpha**3 * abs_t**3) / (denominator * epsilon))
    else:
        denominator = 360.0 if error_mode == "Bound" else 3600.0
        estimate = (alpha**5 * abs_t**5 / (denominator * epsilon)) ** 0.25
    return max(_MIN_STEPS, math.ceil(estimate))


def resolve_suzuki_order(expr: Expr | int, scalars: dict[str, float]) -> int:
    """Resolve `using Suzuki(order = ...)` to an int (LISS-0371).

    Accepts any closed classical scalar expression (literal, named
    constant, prelude constant, simple arithmetic), not just a bare
    literal. Falls back to 2 only when the expression is not resolvable
    (typecheck.py's `_check_suzuki_policy` already rejects an order that
    resolves to neither 2 nor 4, so this fallback is unreachable for a
    program that passed typecheck).
    """
    if isinstance(expr, (int, float)) and not isinstance(expr, bool):
        return int(expr)
    v = _eval_float(expr, scalars)  # type: ignore[arg-type]
    return int(v) if v is not None else 2


def resolve_suzuki_steps(
    policy: SuzukiPolicy, terms: Sequence[PauliTerm], t: float, scalars: dict[str, float]
) -> int:
    """Resolve an AST Suzuki policy after its Hamiltonian is compiled."""
    steps = int(policy.steps.value) if isinstance(policy.steps, LitInt) else None
    tolerance = (
        float(policy.tolerance.value)
        if isinstance(policy.tolerance, (LitInt, LitFloat))
        else None
    )
    order = resolve_suzuki_order(policy.order, scalars)
    return suzuki_step_count(
        terms,
        t,
        tolerance=tolerance,
        error_mode=policy.error_mode,
        steps=steps,
        order=order,
    )


_S4_P = 1.0 / (4.0 - 4.0 ** (1.0 / 3.0))


def suzuki_gates(
    terms: Sequence[PauliTerm],
    t: float,
    site_to_qubit: Sequence[int],
    *,
    steps: int,
    order: int = 2,
) -> list[Gate]:
    """Emit Suzuki S2 or S4 product formula gates (ADR 0084 / LISS-0142)."""
    if steps < 1:
        raise TrotterError("SUZUKI_POLICY_ERROR", "steps must be positive")
    if order not in {2, 4}:
        raise TrotterError("SUZUKI_ORDER_ERROR", "Suzuki supports order 2 or 4")
    n = int(steps)
    dt = float(t) / float(n)
    out: list[Gate] = []
    for step in range(n):
        if order == 2:
            out.extend(_s2_product_gates(terms, dt, site_to_qubit, step, n, label="S2"))
        else:
            p = _S4_P
            # S4(λ) = S2(pλ)^2 S2((1-4p)λ) S2(pλ)^2
            for _ in range(2):
                out.extend(
                    _s2_product_gates(terms, p * dt, site_to_qubit, step, n, label="S4")
                )
            out.extend(
                _s2_product_gates(
                    terms, (1.0 - 4.0 * p) * dt, site_to_qubit, step, n, label="S4"
                )
            )
            for _ in range(2):
                out.extend(
                    _s2_product_gates(terms, p * dt, site_to_qubit, step, n, label="S4")
                )
    if not out:
        q0 = site_to_qubit[0]
        out.append(
            Gate(
                "rz",
                (q0,),
                angle=0.0,
                comment=f"suzuki S{order} N={n} idle/global-phase",
            )
        )
    return out


def _s2_product_gates(
    terms: Sequence[PauliTerm],
    delta: float,
    site_to_qubit: Sequence[int],
    step: int,
    total_steps: int,
    *,
    label: str,
) -> list[Gate]:
    """One symmetric S2 product for duration ``delta``."""
    out: list[Gate] = []
    ordered = list(terms[:-1])
    for term in ordered:
        out.extend(
            _suzuki_term_gates(term, delta / 2.0, site_to_qubit, step, total_steps, label)
        )
    if terms:
        out.extend(
            _suzuki_term_gates(terms[-1], delta, site_to_qubit, step, total_steps, label)
        )
    for term in reversed(ordered):
        out.extend(
            _suzuki_term_gates(term, delta / 2.0, site_to_qubit, step, total_steps, label)
        )
    return out


def _suzuki_term_gates(
    term: PauliTerm,
    delta_t: float,
    site_to_qubit: Sequence[int],
    step: int,
    total_steps: int,
    label: str = "S2",
) -> list[Gate]:
    # ADR 0195 / LISS-0341: no absolute-coefficient pre-filter here -- a
    # real Joule-scale coefficient (~1e-19) is far below any natural-
    # units-era absolute epsilon but is not physically negligible once
    # divided by real hbar below. The dimensionless-theta check after
    # that division is the correct (unit-independent) negligibility test.
    if abs(term.coeff.imag) > 1e-9:
        raise TrotterError(
            REJECT_COMPLEX_COEFF,
            f"non-Hermitian Pauli coeff {term.coeff}",
        )
    if all(kind == "I" for kind in term.kinds):
        return []
    from ...stdlib.prelude import HBAR_SI

    theta = float(term.coeff.real) * delta_t / HBAR_SI
    if abs(theta) < 1e-15:
        return []
    return _pauli_exp_gates(
        term.kinds,
        theta,
        site_to_qubit,
        comment=f"suzuki {label} step {step + 1}/{total_steps} dt={delta_t:.6g}",
    )


def _pauli_exp_gates(
    kinds: tuple[str, ...],
    theta: float,
    site_to_qubit: Sequence[int],
    *,
    comment: str = "",
) -> list[Gate]:
    """Emit gates for exp(-i θ P) with P = ⊗ kinds[site].

    Basis change X→H, Y→rx(π/2); CNOT ladder; rz(2θ); undo.
    OpenQASM rz(φ) = exp(-i φ Z / 2) ⇒ exp(-i θ Z) uses φ = 2θ.
    """
    active: list[tuple[int, str]] = []
    for site, kind in enumerate(kinds):
        k = kind.upper()
        if k == "I":
            continue
        if k not in {"X", "Y", "Z"}:
            raise TrotterError(REJECT_UNSUPPORTED_H, f"unsupported Pauli kind `{kind}`")
        if site >= len(site_to_qubit):
            raise TrotterError(
                REJECT_UNSUPPORTED_H,
                f"Pauli site {site} outside evolve wire count {len(site_to_qubit)}",
            )
        active.append((site_to_qubit[site], k))
    if not active:
        return []

    gates: list[Gate] = []
    # Basis change → Z
    for q, k in active:
        if k == "X":
            gates.append(Gate("h", (q,), comment=comment))
        elif k == "Y":
            gates.append(Gate("rx", (q,), angle=math.pi / 2.0, comment=comment))
    # Parity onto last qubit
    for i in range(len(active) - 1):
        c, t = active[i][0], active[i + 1][0]
        gates.append(Gate("cx", (c, t), comment=comment))
    # Diagonal rotation
    target = active[-1][0]
    gates.append(Gate("rz", (target,), angle=2.0 * theta, comment=comment))
    # Undo CNOTs
    for i in range(len(active) - 2, -1, -1):
        c, t = active[i][0], active[i + 1][0]
        gates.append(Gate("cx", (c, t), comment=comment))
    # Undo basis
    for q, k in active:
        if k == "X":
            gates.append(Gate("h", (q,), comment=comment))
        elif k == "Y":
            gates.append(Gate("rx", (q,), angle=-math.pi / 2.0, comment=comment))
    return gates


def _eval_float(expr: Expr, scalars: dict[str, float]) -> float | None:
    if isinstance(expr, LitFloat):
        return float(expr.value)
    if isinstance(expr, LitInt):
        return float(expr.value)
    if isinstance(expr, Var):
        if expr.name in scalars:
            return float(scalars[expr.name])
        from ...stdlib.prelude import PRELUDE_CONSTANTS

        if expr.name in PRELUDE_CONSTANTS:
            return float(PRELUDE_CONSTANTS[expr.name])
        return None
    if isinstance(expr, Attr):
        base = _eval_float(expr.obj, scalars)
        if base is None:
            return None
        # LISS-0360: defer to dimensions.py's canonical Time scale table
        # instead of a locally-hardcoded, independently-maintained copy --
        # this local copy predates ADR 0195's `ps`/`fs` additions and had
        # silently gone stale.
        from ...dimensions import UNIT_SCALE_TO_CANONICAL

        if expr.name == "s":
            return base
        scale = UNIT_SCALE_TO_CANONICAL.get(expr.name)
        if scale is not None and scale[0] == "s":
            return base * scale[1]
        return None
    if isinstance(expr, BinOp):
        a = _eval_float(expr.lhs, scalars)
        b = _eval_float(expr.rhs, scalars)
        if a is None or b is None:
            return None
        if expr.op == "+":
            return a + b
        if expr.op == "-":
            return a - b
        if expr.op == "*":
            return a * b
        if expr.op == "/":
            if b == 0.0:
                return None
            return a / b
    return None
