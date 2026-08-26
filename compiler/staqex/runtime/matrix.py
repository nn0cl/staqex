"""Dense complex matrices + expm(-i H t / hbar) without NumPy (ADR 0195: real hbar)."""

from __future__ import annotations

import cmath
import math
from typing import Sequence


Matrix = list[list[complex]]


def zeros(n: int) -> Matrix:
    return [[0j] * n for _ in range(n)]


def eye(n: int) -> Matrix:
    m = zeros(n)
    for i in range(n):
        m[i][i] = 1.0 + 0j
    return m


def mat_add(a: Matrix, b: Matrix) -> Matrix:
    n = len(a)
    return [[a[i][j] + b[i][j] for j in range(n)] for i in range(n)]


def mat_scale(a: Matrix, s: complex) -> Matrix:
    n = len(a)
    return [[a[i][j] * s for j in range(n)] for i in range(n)]


def mat_mul(a: Matrix, b: Matrix) -> Matrix:
    n = len(a)
    out = zeros(n)
    for i in range(n):
        for k in range(n):
            aik = a[i][k]
            if aik == 0:
                continue
            for j in range(n):
                out[i][j] += aik * b[k][j]
    return out


def mat_dag(a: Matrix) -> Matrix:
    n = len(a)
    return [[a[j][i].conjugate() for j in range(n)] for i in range(n)]


def apply_mat(m: Matrix, v: list[complex]) -> list[complex]:
    n = len(m)
    return [sum(m[i][j] * v[j] for j in range(n)) for i in range(n)]


def frobenius_norm(a: Matrix) -> float:
    return math.sqrt(sum(abs(a[i][j]) ** 2 for i in range(len(a)) for j in range(len(a))))


def expm_ih(h: Matrix, t: float) -> Matrix:
    """U = exp(-i H t / hbar) via scaling-and-squaring + Taylor (H Hermitian
    assumed; ADR 0195 -- real hbar, H in Joules, t in seconds)."""
    from ..stdlib.prelude import HBAR_SI

    n = len(h)
    # A = -i t H / hbar
    a = mat_scale(h, -1j * float(t) / HBAR_SI)
    # Scale so ||A||/2^s is small. Real hbar division can push ||A|| many
    # orders of magnitude larger than the old hbar=1 convention ever did,
    # so the halving count is computed directly from the norm (standard
    # scaling-and-squaring) rather than a small fixed cap that silently
    # left ||A||/2^s >> 1 and overflowed the Taylor series below.
    norm = frobenius_norm(a)
    s = max(0, math.ceil(math.log2(norm))) if norm > 1.0 else 0
    if s > 0:
        a = mat_scale(a, 2.0**-s)
        norm *= 2.0**-s
    # Taylor of exp(A)
    term = eye(n)
    total = eye(n)
    for k in range(1, 24):
        term = mat_mul(term, a)
        term = mat_scale(term, 1.0 / k)
        total = mat_add(total, term)
        if frobenius_norm(term) < 1e-14:
            break
    # Square s times
    for _ in range(s):
        total = mat_mul(total, total)
    return total


# --- Pauli / Fock builders ---

_PAULI: dict[str, Matrix] = {
    "I": [[1, 0], [0, 1]],
    "X": [[0, 1], [1, 0]],
    "Y": [[0, -1j], [1j, 0]],
    "Z": [[1, 0], [0, -1]],
}


def pauli1(name: str) -> Matrix:
    n = name.upper()
    if n not in _PAULI:
        raise ValueError(f"unknown Pauli `{name}`")
    # copy as complex
    p = _PAULI[n]
    return [[complex(p[i][j]) for j in range(2)] for i in range(2)]


def kron(a: Matrix, b: Matrix) -> Matrix:
    na, nb = len(a), len(b)
    out = zeros(na * nb)
    for i in range(na):
        for j in range(na):
            for k in range(nb):
                for l in range(nb):
                    out[i * nb + k][j * nb + l] = a[i][j] * b[k][l]
    return out


def embed_pauli(n_qubits: int, kind: str, site: int) -> Matrix:
    """I⊗…⊗P⊗…⊗I on site ∈ [0, n_qubits)."""
    if not (0 <= site < n_qubits):
        raise ValueError(f"Pauli site {site} out of range for {n_qubits} qubits")
    mats = [pauli1("I")] * n_qubits
    mats[site] = pauli1(kind)
    acc = mats[0]
    for m in mats[1:]:
        acc = kron(acc, m)
    return acc


def number_op(dim: int) -> Matrix:
    """N |n⟩ = n |n⟩ on {|0⟩…|dim-1⟩}."""
    m = zeros(dim)
    for i in range(dim):
        m[i][i] = complex(i)
    return m


def position_op(dim: int) -> Matrix:
    """Q = (a + a†)/√2 on truncated Fock {|0⟩…|dim-1⟩} (ℏ=m=ω=1)."""
    m = zeros(dim)
    for n in range(dim - 1):
        amp = math.sqrt((n + 1) / 2.0)
        m[n][n + 1] = complex(amp)
        m[n + 1][n] = complex(amp)
    return m


def momentum_op(dim: int) -> Matrix:
    """P = -i(a - a†)/√2 on truncated Fock (ℏ=m=ω=1)."""
    m = zeros(dim)
    for n in range(dim - 1):
        amp = math.sqrt((n + 1) / 2.0)
        m[n][n + 1] = -1j * amp
        m[n + 1][n] = 1j * amp
    return m


def position_grid_op(xs: Sequence[float]) -> Matrix:
    """X_x = diag(x_i) on a position grid."""
    n = len(xs)
    m = zeros(n)
    for i, x in enumerate(xs):
        m[i][i] = complex(float(x))
    return m


def momentum_grid_op(xs: Sequence[float]) -> Matrix:
    """P_x ≈ -i ∂_x via Hermitian central differences (periodic)."""
    n = len(xs)
    if n < 2:
        raise ValueError("position grid needs at least 2 points")
    # Uniform spacing assumed (MVP)
    dx = float(xs[1]) - float(xs[0])
    if abs(dx) < 1e-15:
        raise ValueError("degenerate grid spacing")
    # Check near-uniform
    for i in range(1, n - 1):
        d = float(xs[i + 1]) - float(xs[i])
        if abs(d - dx) > 1e-9 * max(1.0, abs(dx)):
            raise ValueError("Xx/Px MVP requires a uniform position grid")
    m = zeros(n)
    c = -1j / (2.0 * dx)
    for j in range(n):
        jp = (j + 1) % n
        jm = (j - 1) % n
        m[j][jp] = c
        m[j][jm] = -c
    return m


def identity(dim: int) -> Matrix:
    return eye(dim)


def tensor_product_states(
    left: Sequence[tuple[Any, complex]], right: Sequence[tuple[Any, complex]]
) -> list[tuple[tuple[Any, Any], complex]]:
    """(|a⟩⊗|b⟩) amplitude table from marginals (already coherent paths)."""
    out: list[tuple[tuple[Any, Any], complex]] = []
    for va, ca in left:
        for vb, cb in right:
            out.append(((va, vb), ca * cb))
    return out


# late import for type hint only
from typing import Any  # noqa: E402
