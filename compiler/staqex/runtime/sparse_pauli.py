"""Sparse Pauli-sum IR for multi-qubit Hamiltonians (ADR 0050).

Avoids building dense 2^n×2^n U for Schrödinger evolve: store H as
Σ c_k P_k and apply e^{-iHt} via Taylor series on the state vector.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from ..ast_nodes import (
    OpBin,
    OpIdentity,
    OpExpr,
    OpHop,
    OpIndexed,
    OpLit,
    OpNumber,
    OpPauli,
    OpPow,
    OpQuadrature,
    OpVar,
)
from .matrix import Matrix, zeros

# Single-site Pauli multiplication: (phase, kind) = A * B
_PAULI_MUL: dict[tuple[str, str], tuple[complex, str]] = {
    ("I", "I"): (1, "I"),
    ("I", "X"): (1, "X"),
    ("I", "Y"): (1, "Y"),
    ("I", "Z"): (1, "Z"),
    ("X", "I"): (1, "X"),
    ("Y", "I"): (1, "Y"),
    ("Z", "I"): (1, "Z"),
    ("X", "X"): (1, "I"),
    ("Y", "Y"): (1, "I"),
    ("Z", "Z"): (1, "I"),
    ("X", "Y"): (1j, "Z"),
    ("Y", "X"): (-1j, "Z"),
    ("Y", "Z"): (1j, "X"),
    ("Z", "Y"): (-1j, "X"),
    ("Z", "X"): (1j, "Y"),
    ("X", "Z"): (-1j, "Y"),
}


@dataclass(frozen=True)
class PauliTerm:
    """One weighted Pauli string; kinds[i] acts on site i (MSB = site 0)."""

    coeff: complex
    kinds: tuple[str, ...]


SparsePauli = list[PauliTerm]


def compile_sparse_pauli(
    op: OpExpr,
    *,
    env: dict[str, OpExpr],
    scalars: dict[str, float] | None = None,
    n_qubits: int,
) -> SparsePauli:
    """Compile Operator AST → coalesced Pauli sum (qubit Hamiltonians only)."""
    scalars = scalars or {}
    terms = _eval(op, env, scalars, n_qubits)
    return _coalesce(terms)


def matvec(terms: Sequence[PauliTerm], vec: list[complex]) -> list[complex]:
    """Compute H|ψ⟩ for sparse Pauli sum H."""
    n = len(terms[0].kinds) if terms else 0
    dim = len(vec)
    if terms and dim != 2**n:
        raise ValueError(f"vector length {dim} != 2^{n}")
    out = [0j] * dim
    for term in terms:
        if abs(term.coeff) == 0:
            continue
        _apply_term_add(term.kinds, term.coeff, vec, out)
    return out


def expm_ih_apply(
    terms: Sequence[PauliTerm],
    t: float,
    vec: list[complex],
    *,
    max_order: int = 48,
    atol: float = 1e-14,
) -> list[complex]:
    """|ψ'⟩ = exp(-i H t / hbar)|ψ⟩ via Taylor series + sparse matvec (no
    dense U; ADR 0195 -- real hbar, H in Joules, t in seconds).

    Real hbar division can push |t/hbar| * ||H|| many orders of magnitude
    larger than the old hbar=1 convention ever did, well beyond a single
    fixed-order Taylor series' convergence range. Uses the same
    scaling-and-squaring idea as `expm_ih` -- applying the small-step
    propagator `exp(A/2^s)` to the state vector `2^s` times, which is
    mathematically identical to applying `exp(A)` once but converges at
    every step -- with `||H||` bounded via the triangle inequality over
    Pauli-string coefficients (each individual Pauli string has operator
    norm 1). Unlike the dense `expm_ih` (which squares a matrix, O(s) work
    regardless of how large `s` is), this sparse/vector form must apply
    the propagator `2^s` times sequentially -- O(2^s) work -- so `s` is
    capped; beyond the cap this fails closed rather than attempting an
    intractable computation."""
    from ..stdlib.prelude import HBAR_SI

    tt = float(t) / HBAR_SI
    h_norm_bound = sum(abs(term.coeff) for term in terms)
    magnitude = abs(tt) * h_norm_bound
    s = max(0, math.ceil(math.log2(magnitude))) if magnitude > 1.0 else 0
    max_s = 16  # steps = 2**16 = 65536, already a generous, bounded worst case
    if s > max_s:
        raise ValueError(
            f"evolve magnitude |H*t/hbar| ~= 2**{s} exceeds the sparse "
            f"evolution step budget (2**{max_s}) -- H and/or t are not "
            "physically plausible real-unit values. ADR 0195 requires H's "
            "coefficients to already be in real Joules and t in real "
            "seconds by the time they reach `evolve`: if H was built from "
            "dimensionless/natural-unit weights, scale it explicitly first, "
            "e.g. `Energy scale = 1.0.eV to J; Operator H = scale * H_raw` "
            "(the `to` unit-conversion operator), matching the shipped "
            "energy/time unit surface (see any `examples/showcase/*` "
            "program's own H_raw/H two-step pattern)"
        )
    steps = 2**s
    step_tt = tt / steps

    result = list(vec)
    for _ in range(steps):
        total = list(result)
        term_v = list(result)
        for k in range(1, max_order + 1):
            hv = matvec(terms, term_v)
            scale = (-1j * step_tt) / k
            term_v = [scale * x for x in hv]
            total = [a + b for a, b in zip(total, term_v)]
            if sum(abs(x) ** 2 for x in term_v) < atol * atol:
                break
        result = total
    return result


def sparse_to_dense(terms: Sequence[PauliTerm]) -> Matrix:
    """Materialize dense H (tests / small-n checks)."""
    if not terms:
        return [[0j]]
    n = len(terms[0].kinds)
    dim = 2**n
    # Columns: apply H to each basis vector
    h = zeros(dim)
    for j in range(dim):
        e = [0j] * dim
        e[j] = 1 + 0j
        col = matvec(terms, e)
        for i in range(dim):
            h[i][j] = col[i]
    return h


def _coalesce(terms: Sequence[PauliTerm]) -> SparsePauli:
    acc: dict[tuple[str, ...], complex] = {}
    for t in terms:
        acc[t.kinds] = acc.get(t.kinds, 0j) + t.coeff
    if not acc:
        return []
    # ADR 0195: real-unit coefficients (Joules) are routinely far below
    # any fixed absolute epsilon (e.g. 1 eV ~= 1.6e-23 relative to a
    # once-plausible 1e-15 natural-units floor). Scale the drop threshold
    # to the largest coefficient present so genuine floating-point
    # cancellation-to-zero is still coalesced away without zeroing real
    # small-magnitude SI values.
    scale = max(abs(c) for c in acc.values())
    if scale == 0:
        return []
    tol = scale * 1e-12
    return [PauliTerm(coeff=c, kinds=k) for k, c in acc.items() if abs(c) > tol]


def _identity(n: int, coeff: complex = 1 + 0j) -> SparsePauli:
    return [PauliTerm(coeff=coeff, kinds=tuple("I" for _ in range(n)))]


def _eval(
    op: OpExpr,
    env: dict[str, OpExpr],
    scalars: dict[str, float],
    n: int,
) -> SparsePauli:
    if isinstance(op, OpIdentity):
        if op.acting_space is None:
            raise ValueError(
                "IDENTITY_ACTING_SPACE_UNDETERMINED: cannot materialize an "
                "identity without an acting space"
            )
        if op.acting_space != n:
            raise ValueError("identity acting space does not match the target register")
        return [] if op.kind == "sum" else _identity(n)
    if isinstance(op, OpLit):
        return _identity(n, complex(op.value))
    if isinstance(op, OpPauli):
        site = 0 if op.site is None else op.site
        if not (0 <= site < n):
            raise ValueError(f"Pauli site {site} out of range for {n} qubits")
        kinds = ["I"] * n
        kinds[site] = op.kind.upper()
        return [PauliTerm(coeff=1 + 0j, kinds=tuple(kinds))]
    if isinstance(op, OpIndexed):
        if not isinstance(op.base, OpPauli) or not isinstance(op.index, OpLit):
            raise ValueError("indexed sparse Pauli requires a literal site")
        site = int(op.index.value)
        if not (0 <= site < n):
            raise ValueError(f"Pauli site {site} out of range for {n} qubits")
        kinds = ["I"] * n
        kinds[site] = op.base.kind.upper()
        return [PauliTerm(coeff=1 + 0j, kinds=tuple(kinds))]
    if isinstance(op, (OpNumber, OpQuadrature, OpHop)):
        raise ValueError("Fock operators have no sparse Pauli form")
    if isinstance(op, OpVar):
        if op.name in scalars:
            return _identity(n, complex(scalars[op.name]))
        if op.name in env:
            return _eval(env[op.name], env, scalars, n)
        # LISS-0227: unbound P/Q/N are Fock atoms, not sparse Pauli.
        if op.name in {"P", "Q", "N"}:
            raise ValueError("Fock operators have no sparse Pauli form")
        raise ValueError(f"unbound Operator / scalar `{op.name}`")
    if isinstance(op, OpPow):
        base = _eval(op.base, env, scalars, n)
        acc = _identity(n)
        for _ in range(op.exp):
            acc = _mul_sums(acc, base)
        return acc
    if isinstance(op, OpBin):
        if op.op == "+":
            return _eval(op.lhs, env, scalars, n) + _eval(op.rhs, env, scalars, n)
        if op.op == "-":
            rhs = [PauliTerm(coeff=-t.coeff, kinds=t.kinds) for t in _eval(op.rhs, env, scalars, n)]
            return _eval(op.lhs, env, scalars, n) + rhs
        if op.op == "*":
            if isinstance(op.lhs, OpLit):
                return [
                    PauliTerm(coeff=t.coeff * complex(op.lhs.value), kinds=t.kinds)
                    for t in _eval(op.rhs, env, scalars, n)
                ]
            if isinstance(op.rhs, OpLit):
                return [
                    PauliTerm(coeff=t.coeff * complex(op.rhs.value), kinds=t.kinds)
                    for t in _eval(op.lhs, env, scalars, n)
                ]
            if isinstance(op.lhs, OpVar) and op.lhs.name in scalars:
                s = complex(scalars[op.lhs.name])
                return [
                    PauliTerm(coeff=t.coeff * s, kinds=t.kinds)
                    for t in _eval(op.rhs, env, scalars, n)
                ]
            if isinstance(op.rhs, OpVar) and op.rhs.name in scalars:
                s = complex(scalars[op.rhs.name])
                return [
                    PauliTerm(coeff=t.coeff * s, kinds=t.kinds)
                    for t in _eval(op.lhs, env, scalars, n)
                ]
            return _mul_sums(
                _eval(op.lhs, env, scalars, n),
                _eval(op.rhs, env, scalars, n),
            )
    raise ValueError(f"cannot compile sparse Pauli for {type(op).__name__}")


def _mul_sums(a: SparsePauli, b: SparsePauli) -> SparsePauli:
    out: list[PauliTerm] = []
    for ta in a:
        for tb in b:
            out.append(_mul_term(ta, tb))
    return out


def _mul_term(a: PauliTerm, b: PauliTerm) -> PauliTerm:
    if len(a.kinds) != len(b.kinds):
        raise ValueError("Pauli string length mismatch")
    phase = a.coeff * b.coeff
    kinds: list[str] = []
    for ka, kb in zip(a.kinds, b.kinds):
        p, k = _PAULI_MUL[(ka, kb)]
        phase *= p
        kinds.append(k)
    return PauliTerm(coeff=phase, kinds=tuple(kinds))


def _apply_term_add(
    kinds: tuple[str, ...],
    coeff: complex,
    vec: list[complex],
    out: list[complex],
) -> None:
    n = len(kinds)
    for i, amp in enumerate(vec):
        if amp == 0:
            continue
        j = i
        phase = coeff
        for site, p in enumerate(kinds):
            if p == "I":
                continue
            bit_pos = n - 1 - site
            bit = (i >> bit_pos) & 1
            if p == "Z":
                if bit:
                    phase *= -1
            elif p == "X":
                j ^= 1 << bit_pos
            elif p == "Y":
                j ^= 1 << bit_pos
                phase *= 1j if bit == 0 else -1j
            else:
                raise ValueError(f"unknown Pauli `{p}`")
        out[j] += phase * amp
