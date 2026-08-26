"""Compile Operator AST → dense Hamiltonian matrix (real hbar, ADR 0195)."""

from __future__ import annotations

from typing import Sequence

from ..ast_nodes import (
    OpBin,
    OpExpr,
    OpGridQuad,
    OpHop,
    OpIdentity,
    OpIndexed,
    OpLit,
    OpNumber,
    OpPauli,
    OpPow,
    OpQuadrature,
    OpVar,
)
from .matrix import (
    Matrix,
    embed_pauli,
    eye,
    identity,
    mat_add,
    mat_mul,
    mat_scale,
    momentum_grid_op,
    momentum_op,
    number_op,
    pauli1,
    position_grid_op,
    position_op,
)


def hop_basis_dim(
    op: OpExpr,
    env: dict[str, OpExpr],
    scalars: dict[str, float] | None = None,
) -> int:
    """Minimal site-basis dimension implied by `hop(i,j)` (max index + 1)."""
    scalars = scalars or {}
    hi = -1

    def walk(e: OpExpr) -> None:
        nonlocal hi
        if isinstance(e, OpHop):
            hi = max(hi, e.i, e.j)
        elif isinstance(e, OpBin):
            walk(e.lhs)
            walk(e.rhs)
        elif isinstance(e, OpPow):
            walk(e.base)
        elif isinstance(e, OpVar):
            if e.name in scalars:
                return
            if e.name in env:
                walk(env[e.name])

    walk(op)
    return hi + 1 if hi >= 0 else 0


def op_n_qubits(
    op: OpExpr,
    env: dict[str, OpExpr],
    scalars: dict[str, float] | None = None,
) -> int:
    """Infer space size: >0 qubits, 0 Fock, -1 position grid."""
    if isinstance(op, OpIdentity):
        if op.acting_space is None:
            raise ValueError(
                "IDENTITY_ACTING_SPACE_UNDETERMINED: cannot determine the space "
                "this identity acts on; specify QubitRegister<N>"
            )
        return op.acting_space
    mode = op_space(op, env, scalars)
    if mode == "fock":
        return 0
    if mode == "grid":
        return -1
    # qubit
    scalars = scalars or {}
    sites: list[int] = []
    explicit_spaces: list[int] = []

    def walk(e: OpExpr) -> None:
        if isinstance(e, OpIdentity):
            if e.acting_space is None:
                raise ValueError(
                    "IDENTITY_ACTING_SPACE_UNDETERMINED: cannot determine the "
                    "space this identity acts on; specify QubitRegister<N>"
                )
            explicit_spaces.append(e.acting_space)
        elif isinstance(e, OpPauli):
            if e.site is not None:
                sites.append(e.site)
        elif isinstance(e, OpIndexed):
            if isinstance(e.base, OpPauli) and isinstance(e.index, OpLit):
                sites.append(int(e.index.value))
        elif isinstance(e, OpBin):
            walk(e.lhs)
            walk(e.rhs)
        elif isinstance(e, OpPow):
            walk(e.base)
        elif isinstance(e, OpVar):
            if e.name in scalars:
                return
            if e.name in env:
                walk(env[e.name])
                return
            builtin = _builtin_op_atom(e.name, e.span)
            if builtin is not None:
                walk(builtin)
                return
            raise ValueError(f"unbound Operator / scalar `{e.name}`")

    walk(op)
    if explicit_spaces:
        site_space = max(sites) + 1 if sites else 0
        return max(max(explicit_spaces), site_space)
    if sites:
        return max(sites) + 1
    return 1  # bare X/Y/Z


def op_space(
    op: OpExpr,
    env: dict[str, OpExpr],
    scalars: dict[str, float] | None = None,
) -> str:
    """Return `fock` | `grid` | `qubit` for an Operator polynomial.

    Context rule (ADR 0053):
    - Fock: `N` / `Q` (and `P` with them), or tight-binding `hop(i,j)`
    - Position grid: bare `X` (no site) with `P`, no `Y`/`Z`/`N`/`Q`/sites
    - Qubit: Pauli `X,Y,Z,I` (optional sites)
    """
    scalars = scalars or {}
    uses_n = False
    uses_q = False
    uses_p = False
    uses_bare_x = False
    uses_yz = False
    uses_hop = False
    sites: list[int] = []
    legacy_grid = False

    def walk(e: OpExpr) -> None:
        nonlocal uses_n, uses_q, uses_p, uses_bare_x, uses_yz, uses_hop, legacy_grid
        if isinstance(e, OpPauli):
            if e.site is not None:
                sites.append(e.site)
            elif e.kind == "X":
                uses_bare_x = True
            elif e.kind in {"Y", "Z"}:
                uses_yz = True
        elif isinstance(e, OpIndexed):
            if isinstance(e.base, OpPauli) and isinstance(e.index, OpLit):
                sites.append(int(e.index.value))
                if e.base.kind in {"Y", "Z"}:
                    uses_yz = True
        elif isinstance(e, OpNumber):
            uses_n = True
        elif isinstance(e, OpHop):
            uses_hop = True
        elif isinstance(e, OpQuadrature):
            if e.kind == "Q":
                uses_q = True
            elif e.kind == "P":
                uses_p = True
        elif isinstance(e, OpGridQuad):
            legacy_grid = True
        elif isinstance(e, OpBin):
            walk(e.lhs)
            walk(e.rhs)
        elif isinstance(e, OpPow):
            walk(e.base)
        elif isinstance(e, OpVar):
            if e.name in scalars:
                return
            if e.name in env:
                walk(env[e.name])
                return
            builtin = _builtin_op_atom(e.name, e.span)
            if builtin is not None:
                walk(builtin)
                return
            raise ValueError(f"unbound Operator / scalar `{e.name}`")

    walk(op)
    if legacy_grid:
        return "grid"
    fockish = (
        uses_n
        or uses_q
        or uses_hop
        or (uses_p and not uses_bare_x and not uses_yz and not sites)
    )
    # Position-grid HO: H = ½(P² + X²) — bare X + P, no Y/Z/N/Q/sites
    gridish = (
        uses_bare_x
        and uses_p
        and not uses_yz
        and not uses_n
        and not uses_q
        and not uses_hop
        and not sites
    )
    if (uses_n or uses_q or uses_hop) and (gridish or sites or uses_yz):
        raise ValueError("cannot mix Fock N/Q/hop with grid X/P or site Pauli (MVP)")
    if gridish and (uses_n or uses_q or uses_hop or sites or uses_yz):
        raise ValueError("cannot mix position-grid X/P with Fock or site Pauli (MVP)")
    if fockish and not gridish:
        return "fock"
    if gridish:
        return "grid"
    return "qubit"


def compile_hamiltonian(
    op: OpExpr,
    *,
    env: dict[str, OpExpr],
    scalars: dict[str, float] | None = None,
    n_qubits: int | None = None,
    fock_dim: int | None = None,
    grid_xs: Sequence[float] | None = None,
) -> Matrix:
    scalars = scalars or {}
    if n_qubits is None:
        nq = op_n_qubits(op, env, scalars)
    else:
        nq = n_qubits
    if nq == 0:
        dim = fock_dim if fock_dim is not None else 4
        return _eval_fock(op, env, scalars, dim)
    if nq < 0:
        if grid_xs is None:
            raise ValueError("grid Hamiltonian requires grid_xs abscissae")
        return _eval_grid(op, env, scalars, list(grid_xs))
    return _eval_qubits(op, env, scalars, nq)


def _builtin_op_atom(name: str, span) -> OpExpr | None:
    """ADR 0049 / 0041 atoms when no local Operator binding shadows them."""
    if name == "N":
        return OpNumber(span=span)
    if name == "Q":
        return OpQuadrature(kind="Q", span=span)
    if name == "P":
        return OpQuadrature(kind="P", span=span)
    return None


def _resolve_var(
    op: OpVar, env: dict[str, OpExpr], scalars: dict[str, float]
) -> OpExpr | float:
    if op.name in scalars:
        return scalars[op.name]
    if op.name in env:
        return env[op.name]
    builtin = _builtin_op_atom(op.name, op.span)
    if builtin is not None:
        return builtin
    raise ValueError(f"unbound Operator / scalar `{op.name}`")


def _eval_qubits(
    op: OpExpr, env: dict[str, OpExpr], scalars: dict[str, float], n: int
) -> Matrix:
    if isinstance(op, OpIdentity):
        if op.acting_space is None:
            raise ValueError(
                "IDENTITY_ACTING_SPACE_UNDETERMINED: cannot materialize an "
                "identity without an acting space"
            )
        if op.acting_space != n:
            raise ValueError("identity acting space does not match the target register")
        if op.kind == "Sigma":
            return mat_scale(eye(2**n), 0.0)
        return eye(2**n)
    if isinstance(op, OpLit):
        return mat_scale(eye(2**n), complex(op.value))
    if isinstance(op, OpPauli):
        site = 0 if op.site is None else op.site
        if n == 1 and op.site is None:
            return pauli1(op.kind)
        return embed_pauli(n, op.kind, site)
    if isinstance(op, OpIndexed):
        if not isinstance(op.base, OpPauli) or not isinstance(op.index, OpLit):
            raise ValueError("indexed qubit Pauli requires a literal site")
        site = int(op.index.value)
        if not (0 <= site < n):
            raise ValueError(f"Pauli site {site} out of range for {n} qubits")
        return embed_pauli(n, op.base.kind, site)
    if isinstance(op, OpNumber):
        raise ValueError("N is only valid in Fock Hamiltonians")
    if isinstance(op, OpQuadrature):
        raise ValueError("Q/P are only valid in Fock Hamiltonians")
    if isinstance(op, OpGridQuad):
        raise ValueError("Xx/Px are only valid in grid Hamiltonians")
    if isinstance(op, OpVar):
        resolved = _resolve_var(op, env, scalars)
        if isinstance(resolved, float):
            return mat_scale(eye(2**n), complex(resolved))
        return _eval_qubits(resolved, env, scalars, n)
    if isinstance(op, OpPow):
        base = _eval_qubits(op.base, env, scalars, n)
        acc = eye(2**n)
        for _ in range(op.exp):
            acc = mat_mul(acc, base)
        return acc
    if isinstance(op, OpBin):
        if op.op == "+":
            return mat_add(
                _eval_qubits(op.lhs, env, scalars, n),
                _eval_qubits(op.rhs, env, scalars, n),
            )
        if op.op == "-":
            return mat_add(
                _eval_qubits(op.lhs, env, scalars, n),
                mat_scale(_eval_qubits(op.rhs, env, scalars, n), -1),
            )
        if op.op == "*":
            if isinstance(op.lhs, OpLit):
                return mat_scale(
                    _eval_qubits(op.rhs, env, scalars, n), complex(op.lhs.value)
                )
            if isinstance(op.rhs, OpLit):
                return mat_scale(
                    _eval_qubits(op.lhs, env, scalars, n), complex(op.rhs.value)
                )
            if isinstance(op.lhs, OpVar) and op.lhs.name in scalars:
                return mat_scale(
                    _eval_qubits(op.rhs, env, scalars, n),
                    complex(scalars[op.lhs.name]),
                )
            if isinstance(op.rhs, OpVar) and op.rhs.name in scalars:
                return mat_scale(
                    _eval_qubits(op.lhs, env, scalars, n),
                    complex(scalars[op.rhs.name]),
                )
            return mat_mul(
                _eval_qubits(op.lhs, env, scalars, n),
                _eval_qubits(op.rhs, env, scalars, n),
            )
    raise ValueError(f"cannot compile operator node {type(op).__name__}")


def _hop_matrix(dim: int, i: int, j: int) -> Matrix:
    """Dense |i⟩⟨j| on a `dim`-site basis."""
    if not (0 <= i < dim and 0 <= j < dim):
        raise ValueError(f"hop({i},{j}) out of range for dim={dim}")
    out = [[0j] * dim for _ in range(dim)]
    out[i][j] = 1 + 0j
    return out


def _eval_fock(
    op: OpExpr, env: dict[str, OpExpr], scalars: dict[str, float], dim: int
) -> Matrix:
    if isinstance(op, OpLit):
        return mat_scale(identity(dim), complex(op.value))
    if isinstance(op, OpNumber):
        return number_op(dim)
    if isinstance(op, OpHop):
        return _hop_matrix(dim, op.i, op.j)
    if isinstance(op, OpQuadrature):
        if op.kind == "Q":
            return position_op(dim)
        if op.kind == "P":
            return momentum_op(dim)
        raise ValueError(f"unknown quadrature `{op.kind}`")
    if isinstance(op, OpPauli):
        raise ValueError("Pauli not valid in Fock H (use N / Q / P / hop)")
    if isinstance(op, OpGridQuad):
        raise ValueError("Xx/Px not valid in Fock H (use grid evolve)")
    if isinstance(op, OpVar):
        resolved = _resolve_var(op, env, scalars)
        if isinstance(resolved, float):
            return mat_scale(identity(dim), complex(resolved))
        return _eval_fock(resolved, env, scalars, dim)
    if isinstance(op, OpPow):
        base = _eval_fock(op.base, env, scalars, dim)
        acc = identity(dim)
        for _ in range(op.exp):
            acc = mat_mul(acc, base)
        return acc
    if isinstance(op, OpBin):
        if op.op == "+":
            return mat_add(
                _eval_fock(op.lhs, env, scalars, dim),
                _eval_fock(op.rhs, env, scalars, dim),
            )
        if op.op == "-":
            return mat_add(
                _eval_fock(op.lhs, env, scalars, dim),
                mat_scale(_eval_fock(op.rhs, env, scalars, dim), -1),
            )
        if op.op == "*":
            if isinstance(op.lhs, OpLit):
                return mat_scale(
                    _eval_fock(op.rhs, env, scalars, dim), complex(op.lhs.value)
                )
            if isinstance(op.rhs, OpLit):
                return mat_scale(
                    _eval_fock(op.lhs, env, scalars, dim), complex(op.rhs.value)
                )
            if isinstance(op.lhs, OpVar) and op.lhs.name in scalars:
                return mat_scale(
                    _eval_fock(op.rhs, env, scalars, dim),
                    complex(scalars[op.lhs.name]),
                )
            if isinstance(op.rhs, OpVar) and op.rhs.name in scalars:
                return mat_scale(
                    _eval_fock(op.lhs, env, scalars, dim),
                    complex(scalars[op.rhs.name]),
                )
            return mat_mul(
                _eval_fock(op.lhs, env, scalars, dim),
                _eval_fock(op.rhs, env, scalars, dim),
            )
    raise ValueError(f"cannot compile Fock operator {type(op).__name__}")


def _eval_grid(
    op: OpExpr,
    env: dict[str, OpExpr],
    scalars: dict[str, float],
    xs: list[float],
) -> Matrix:
    dim = len(xs)
    if isinstance(op, OpLit):
        return mat_scale(identity(dim), complex(op.value))
    # Context: bare X → x̂, P → p̂ = -i∂_x (ADR 0053)
    if isinstance(op, OpPauli) and op.kind == "X" and op.site is None:
        return position_grid_op(xs)
    if isinstance(op, OpQuadrature) and op.kind == "P":
        return momentum_grid_op(xs)
    if isinstance(op, OpGridQuad):
        if op.kind == "Xx":
            return position_grid_op(xs)
        if op.kind == "Px":
            return momentum_grid_op(xs)
        raise ValueError(f"unknown legacy grid quadrature `{op.kind}`")
    if isinstance(op, OpPauli):
        raise ValueError("only bare X (position) is valid with P on a Position grid")
    if isinstance(op, (OpNumber, OpQuadrature)):
        raise ValueError("Fock N/Q not valid in Position-grid H (use X and P)")
    if isinstance(op, OpVar):
        resolved = _resolve_var(op, env, scalars)
        if isinstance(resolved, float):
            return mat_scale(identity(dim), complex(resolved))
        return _eval_grid(resolved, env, scalars, xs)
    if isinstance(op, OpPow):
        base = _eval_grid(op.base, env, scalars, xs)
        acc = identity(dim)
        for _ in range(op.exp):
            acc = mat_mul(acc, base)
        return acc
    if isinstance(op, OpBin):
        if op.op == "+":
            return mat_add(
                _eval_grid(op.lhs, env, scalars, xs),
                _eval_grid(op.rhs, env, scalars, xs),
            )
        if op.op == "-":
            return mat_add(
                _eval_grid(op.lhs, env, scalars, xs),
                mat_scale(_eval_grid(op.rhs, env, scalars, xs), -1),
            )
        if op.op == "*":
            if isinstance(op.lhs, OpLit):
                return mat_scale(
                    _eval_grid(op.rhs, env, scalars, xs), complex(op.lhs.value)
                )
            if isinstance(op.rhs, OpLit):
                return mat_scale(
                    _eval_grid(op.lhs, env, scalars, xs), complex(op.rhs.value)
                )
            if isinstance(op.lhs, OpVar) and op.lhs.name in scalars:
                return mat_scale(
                    _eval_grid(op.rhs, env, scalars, xs),
                    complex(scalars[op.lhs.name]),
                )
            if isinstance(op.rhs, OpVar) and op.rhs.name in scalars:
                return mat_scale(
                    _eval_grid(op.lhs, env, scalars, xs),
                    complex(scalars[op.rhs.name]),
                )
            return mat_mul(
                _eval_grid(op.lhs, env, scalars, xs),
                _eval_grid(op.rhs, env, scalars, xs),
            )
    raise ValueError(f"cannot compile grid operator {type(op).__name__}")
