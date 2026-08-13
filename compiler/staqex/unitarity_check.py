"""Static unitarity / isometry guards (ADR 0045, extended ADR 0052).

Catches clear non-unitary remaps on quantum lineages, non-unitary
Operator matrices on `apply` / `capply` / `ocapply`, Fock/grid Operators
misused as gates, bit-support-collapsing `map`, and non-Hermitian `evolve`.
Full proof of every pushforward remains Deferred.
"""

from __future__ import annotations

from typing import Any, Iterator

from .ast_nodes import (
    Attr,
    BinOp,
    Call,
    Coin,
    CompilationUnit,
    Dirac,
    EvolveExpr,
    Expr,
    FunDecl,
    Inspect,
    KetLit,
    KetSumBinder,
    Lambda,
    LitBool,
    LitFloat,
    LitInt,
    LitString,
    Measure,
    Pipe,
    ReturnStmt,
    Snapshot,
    StateBind,
    SuperposeExpr,
    TensorExpr,
    TupleExpr,
    UnaryNot,
    Var,
    WhenExpr,
)
from .runtime.hamiltonian import compile_hamiltonian, op_n_qubits
from .runtime.matrix import mat_dag, mat_mul
from .runtime.unitaries import named_gate_matrix, rotation_gate_matrix
from .static_operator_resolution import collect_static_operator_context, resolve_static_operator

_EPS = 1e-8

# Ops that mark a coherent quantum lineage (ket / gate / walk)
_QUANTUM_OPS = frozenset(
    {
        "apply",
        "capply",
        "controlled",
        "ocapply",
        "toffoli",
        "hadamard",
        "cnot",
        "phase",
        "grover_diffuse",
        "diffuse",
        "interfer",
        "walk_shift",
        "shift",
        "wavepacket",
        "prepare_selection",
    }
)

# Stricter: non-unitary filters banned only on these (not phase-on-coin pedagogy)
_STRICT_QUANTUM_OPS = frozenset(
    {
        "apply",
        "capply",
        "ocapply",
        "toffoli",
        "hadamard",
        "cnot",
        "interfer",
        "walk_shift",
        "wavepacket",
    }
)


def check_unitarity(unit: CompilationUnit) -> list[dict[str, Any]]:
    diags: list[dict[str, Any]] = []
    if unit.main is None:
        return diags

    from .ast_nodes import FunDecl

    # LISS-0411: struct-of-literals constant folding (ADR 0206 completion
    # for this static-only pass -- no live Evaluator state exists here).
    _, _, objects = collect_static_operator_context(unit)

    operators: dict[str, Any] = {}
    from .stdlib.prelude import PRELUDE_CONSTANTS

    scalars: dict[str, float] = dict(PRELUDE_CONSTANTS)
    quantum: dict[str, bool] = {}  # coherent (incl. phase)
    strict: dict[str, bool] = {}  # ket / gates / interfer
    classical: dict[str, bool] = {}  # expect / Float scalars — not measurable
    for name in PRELUDE_CONSTANTS:
        classical[name] = True

    # Library functions: check Operator locals inside their own lexical scope.
    for decl in unit.decls:
        if not isinstance(decl, FunDecl):
            continue
        local_operators: dict[str, Any] = {}
        for stmt in decl.body.stmts:
            if not isinstance(stmt, StateBind):
                continue
            if stmt.ty is not None and stmt.ty.name == "Operator":
                if len(stmt.names) == 1:
                    local_operators[stmt.names[0]] = stmt.expr
                continue
            _check_expr_unitarity(
                stmt.expr, quantum, strict, local_operators, scalars, objects, unit, diags
            )

    for stmt in unit.main.body.stmts:
        if not isinstance(stmt, StateBind):
            if isinstance(stmt, Measure):
                _check_measure_target(stmt.expr, classical, diags)
                _check_expr_unitarity(
                    stmt.expr, quantum, strict, operators, scalars, objects, unit, diags
                )
            elif isinstance(stmt, Snapshot):
                _check_expr_unitarity(
                    stmt.expr, quantum, strict, operators, scalars, objects, unit, diags
                )
            continue
        if stmt.ty is not None and stmt.ty.name == "Operator":
            if len(stmt.names) == 1:
                operators[stmt.names[0]] = stmt.expr
            continue
        if (
            stmt.ty is not None
            and stmt.ty.name not in {"State", "Operator", "Delta"}
            and len(stmt.names) == 1
            and _is_numeric_lit(stmt.expr)
        ):
            scalars[stmt.names[0]] = float(_lit_value(stmt.expr))
            classical[stmt.names[0]] = True

        q = _expr_is_quantum(stmt.expr, quantum, strict_mode=False)
        s = _expr_is_quantum(stmt.expr, strict, strict_mode=True)
        is_class = _expr_is_classical_scalar(stmt.expr, classical)
        for n in stmt.names:
            quantum[n] = q
            strict[n] = s
            if is_class:
                classical[n] = True

        _check_expr_unitarity(
            stmt.expr, quantum, strict, operators, scalars, objects, unit, diags
        )

    return diags


def _check_measure_target(
    expr: Expr, classical: dict[str, bool], diags: list[dict[str, Any]]
) -> None:
    if isinstance(expr, Var) and classical.get(expr.name, False):
        diags.append(
            {
                "code": "CANNOT_MEASURE_CLASSICAL_VALUE_ERROR",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": (
                    f"`measure` cannot act on classical scalar / elaboration "
                    f"coefficient `{expr.name}` "
                    f"(e.g. ⟨O⟩ from `expect` or Type-First `Float J`). "
                    f"`measure` is Born collapse on a quantum State; "
                    f"classical values are already definite (ADR 0114)."
                ),
            }
        )
    if isinstance(expr, Call) and _op_name(expr) == "expect":
        diags.append(
            {
                "code": "CANNOT_MEASURE_CLASSICAL_VALUE_ERROR",
                "line": expr.span.line,
                "col": expr.span.col,
                "message": (
                    "`measure(expect(...))` is illegal: ⟨O⟩ is a classical scalar, "
                    "not a quantum State."
                ),
            }
        )


def _expr_is_classical_scalar(expr: Expr, classical: dict[str, bool]) -> bool:
    if isinstance(expr, Var):
        return classical.get(expr.name, False)
    if isinstance(expr, Call) and _op_name(expr) == "expect":
        return True
    if isinstance(expr, (LitInt, LitFloat, LitBool)):
        return True
    if isinstance(expr, Inspect):
        return _expr_is_classical_scalar(expr.expr, classical)
    return False


def _check_expr_unitarity(
    expr: Expr,
    quantum: dict[str, bool],
    strict: dict[str, bool],
    operators: dict[str, Any],
    scalars: dict[str, float],
    objects: dict[str, Any],
    unit: CompilationUnit,
    diags: list[dict[str, Any]],
) -> None:
    if isinstance(expr, Call):
        op = _op_name(expr)
        if op == "project" and expr.args:
            src = expr.args[0]
            tgt = expr.args[1] if len(expr.args) > 1 else None
            if isinstance(tgt, Lambda):
                diags.append(
                    {
                        "code": "PREDICATE_PROJECTOR_ERROR",
                        "line": expr.span.line,
                        "col": expr.span.col,
                        "message": (
                            "`project` is the Hilbert projector |k⟩⟨k|, not a "
                            "classical predicate filter. Write project(psi, 0) or "
                            "project(psi, |0>)."
                        ),
                    }
                )
            elif not _expr_is_quantum(src, quantum, strict_mode=False) and not _expr_is_quantum(
                src, strict, strict_mode=True
            ):
                # classical coin / non-quantum carrier
                if isinstance(src, Var) and not quantum.get(src.name, False) and not strict.get(
                    src.name, False
                ):
                    # allow if somehow quantum via ket lineage stored in quantum map
                    pass
                if isinstance(src, (Coin,)) or (
                    isinstance(src, Var)
                    and not quantum.get(src.name, False)
                    and not strict.get(src.name, False)
                ):
                    diags.append(
                        {
                            "code": "PREDICATE_PROJECTOR_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": (
                                "`project` requires a quantum State (Hilbert space). "
                                "Classical `coin()` filters are forbidden."
                            ),
                        }
                    )
            # Hilbert project on quantum with basis label is allowed (not an error)
        if op == "map" and len(expr.args) >= 2:
            src, fn = expr.args[0], expr.args[1]
            if _expr_is_quantum(src, strict, strict_mode=True):
                if _lambda_is_constant(fn) or _lambda_collapses_bits(fn):
                    diags.append(
                        {
                            "code": "NON_UNITARY_TRANSFORM_ERROR",
                            "line": expr.span.line,
                            "col": expr.span.col,
                            "message": (
                                "`map` on a quantum State collapses distinct bit "
                                "labels (non-injective / non-isometric). Use a "
                                "bijective remap or a unitary (`apply`)."
                            ),
                        }
                    )
        if op in {"apply", "capply", "ocapply"} and expr.args:
            if op == "apply":
                u_expr = expr.args[0]
                n_wires = len(expr.args) - 1
            else:
                u_idx = None
                for i, a in enumerate(expr.args):
                    if isinstance(a, Var) and (
                        a.name in operators or named_gate_matrix(a.name) is not None
                    ):
                        u_idx = i
                        break
                if u_idx is None or u_idx < 1 or u_idx >= len(expr.args) - 1:
                    u_expr = None
                    n_wires = 0
                else:
                    u_expr = expr.args[u_idx]
                    n_wires = len(expr.args) - u_idx - 1
            if u_expr is not None and n_wires >= 1:
                _check_apply_unitary(u_expr, n_wires, operators, scalars, objects, unit, diags, expr)
        for a in expr.args:
            _check_expr_unitarity(a, quantum, strict, operators, scalars, objects, unit, diags)
        return

    if isinstance(expr, WhenExpr):
        if _expr_is_quantum(expr.ctrl, strict, strict_mode=True) and _when_collapses(
            expr
        ):
            diags.append(
                {
                    "code": "NON_UNITARY_TRANSFORM_ERROR",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": (
                        "`mix` on a quantum control maps distinct arms to the same "
                        "value (non-injective / non-unitary). Prefer `apply` / `capply`."
                    ),
                }
            )
        _check_expr_unitarity(expr.ctrl, quantum, strict, operators, scalars, objects, unit, diags)
        for arm in expr.arms:
            _check_expr_unitarity(
                arm.body, quantum, strict, operators, scalars, objects, unit, diags
            )
        return

    if isinstance(expr, EvolveExpr) and expr.hamiltonian is not None:
        hop = expr.hamiltonian
        if isinstance(hop, Var) and hop.name in operators:
            _check_hamiltonian_hermitian(
                hop.name, operators[hop.name], operators, scalars, objects, unit, diags, expr
            )
        for s in expr.seeds:
            _check_expr_unitarity(s, quantum, strict, operators, scalars, objects, unit, diags)
        return

    if isinstance(expr, EvolveExpr) and expr.hamiltonian is None and expr.body is not None:
        # LISS-0436: `Evolve (vars) times N { block }` has no Hamiltonian to
        # check Hermiticity of -- unlike the `under H for dur` branch above,
        # nothing here previously verified the block's own content at all
        # (it fell through to the generic `_children` walk, which only finds
        # *nested* Evolve/apply/map/etc. sites to check, never asks whether
        # the block itself is built from anything trustworthy). A block that
        # calls an arbitrary user function is opaque: that function's own
        # body is never inspected, so nothing here actually guarantees the
        # block is a coherent transform at all. Require every `lets`/`result`
        # expression to be built only from State arithmetic/tensor-products
        # and calls to the closed, already-unitarity-checked vocabulary
        # (`_QUANTUM_OPS`) or to another user function whose own body
        # satisfies this same constraint, recursively -- fail closed
        # (`EVOLVE_BLOCK_OPAQUE_TRANSFORM`) on anything else, rather than
        # silently trusting it.
        verified: dict[str, bool] = {}
        transparent = True
        for lb in expr.body.lets:
            if not _expr_is_transparent(lb.expr, unit, verified, frozenset()):
                transparent = False
                break
        if transparent and not _expr_is_transparent(
            expr.body.result, unit, verified, frozenset()
        ):
            transparent = False
        if not transparent:
            diags.append(
                {
                    "code": "EVOLVE_BLOCK_OPAQUE_TRANSFORM",
                    "line": expr.span.line,
                    "col": expr.span.col,
                    "message": (
                        "`Evolve (...) times N { ... }`'s block must be built "
                        "only from State arithmetic/tensor-products and calls "
                        "to an already-unitarity-checked primitive (apply/"
                        "capply/controlled/walk_shift/...) or a user function "
                        "whose own body satisfies the same constraint -- an "
                        "opaque call whose body is not itself verified is not "
                        "allowed here."
                    ),
                }
            )
        for s in expr.seeds:
            _check_expr_unitarity(s, quantum, strict, operators, scalars, objects, unit, diags)
        return

    for child in _children(expr):
        _check_expr_unitarity(child, quantum, strict, operators, scalars, objects, unit, diags)


def _expr_is_transparent(
    expr: Expr,
    unit: CompilationUnit,
    verified: dict[str, bool],
    in_progress: frozenset[str],
) -> bool:
    """LISS-0436: does `expr` denote a coherent transform built only from
    State arithmetic/tensor-products, literals, and calls to either the
    closed `_QUANTUM_OPS` vocabulary or a user function whose own body
    satisfies this same constraint (checked recursively)? Fails closed
    (`False`) on anything else -- a classical control-flow construct
    (`WhenExpr`/`Mix`, `Pipe`, ...) or a call to an unrecognized/unverified
    callee -- rather than assuming it's safe."""
    if isinstance(expr, (Var, LitInt, LitFloat, LitBool, LitString, KetLit)):
        return True
    if isinstance(expr, BinOp):
        return _expr_is_transparent(
            expr.lhs, unit, verified, in_progress
        ) and _expr_is_transparent(expr.rhs, unit, verified, in_progress)
    if isinstance(expr, TensorExpr):
        return _expr_is_transparent(
            expr.left, unit, verified, in_progress
        ) and _expr_is_transparent(expr.right, unit, verified, in_progress)
    if isinstance(expr, TupleExpr):
        return all(_expr_is_transparent(it, unit, verified, in_progress) for it in expr.items)
    if isinstance(expr, Attr):
        return _expr_is_transparent(expr.obj, unit, verified, in_progress)
    if isinstance(expr, Call):
        name = _op_name(expr)
        args_ok = all(
            _expr_is_transparent(a, unit, verified, in_progress) for a in expr.args
        )
        if not args_ok:
            return False
        if name in _QUANTUM_OPS:
            return True
        return _fn_body_is_transparent(name, unit, verified, in_progress)
    return False


def _fn_body_is_transparent(
    name: str,
    unit: CompilationUnit,
    verified: dict[str, bool],
    in_progress: frozenset[str],
) -> bool:
    """Recursively verify a user-defined function's own body, memoizing by
    name (`verified`) and guarding against a call cycle (`in_progress` --
    a function already being verified higher up the same recursion stack
    is provisionally trusted, matching how a genuinely-cyclic pair of
    mutually-recursive transforms would still each individually reduce to
    the same closed vocabulary at their own base case)."""
    if name in verified:
        return verified[name]
    if name in in_progress:
        return True
    fn = next(
        (
            d
            for d in unit.decls
            if isinstance(d, FunDecl) and d.name == name
        ),
        None,
    )
    if fn is None:
        return False
    next_in_progress = in_progress | {name}
    ok = True
    for stmt in fn.body.stmts:
        if isinstance(stmt, StateBind):
            if stmt.ty is not None and stmt.ty.name == "Operator":
                # An Operator-typed bind constructs matrix/Hamiltonian
                # *data* (Pauli-atom OpBin/OpVar trees, a different AST
                # family from the general expression grammar this check
                # otherwise walks) -- it doesn't act on a State by itself,
                # so it isn't a "transform" this check needs to verify.
                # Its actual use (`apply(CoinOp, c)`) is what matters, and
                # that call site is already checked as an ordinary Call
                # below; `_check_apply_unitary` independently verifies the
                # matrix itself is unitary. Matches `check_unitarity`'s own
                # top-level loop, which skips Operator binds the same way.
                continue
            if not _expr_is_transparent(stmt.expr, unit, verified, next_in_progress):
                ok = False
                break
        elif isinstance(stmt, ReturnStmt):
            if not _expr_is_transparent(stmt.expr, unit, verified, next_in_progress):
                ok = False
                break
        else:
            ok = False
            break
    verified[name] = ok
    return ok


def _check_apply_unitary(
    u_expr: Expr,
    n_wires: int,
    operators: dict[str, Any],
    scalars: dict[str, float],
    objects: dict[str, Any],
    unit: CompilationUnit,
    diags: list[dict[str, Any]],
    site: Expr,
) -> None:
    try:
        if isinstance(u_expr, Call) and isinstance(u_expr.callee, Var):
            op = u_expr.callee.name.lower()
            if op in {"rx", "ry", "rz"} and n_wires == 1 and len(u_expr.args) == 1:
                # Angle closedness checked at runtime; assume unitary shape
                theta = 0.0
                arg = u_expr.args[0]
                if isinstance(arg, (LitInt, LitFloat)):
                    theta = float(arg.value)
                elif isinstance(arg, Var) and arg.name in scalars:
                    theta = float(scalars[arg.name])
                mat = rotation_gate_matrix(op[1], theta)
                if not _is_unitary(mat):
                    diags.append(
                        {
                            "code": "NON_UNITARY_TRANSFORM_ERROR",
                            "line": site.span.line,
                            "col": site.span.col,
                            "message": f"`{op}(θ)` matrix is not unitary",
                        }
                    )
            return
        if not isinstance(u_expr, Var):
            return
        name = u_expr.name
        if name in operators:
            # LISS-0411: resolve struct-field coefficients before
            # op_n_qubits/compile_hamiltonian, which don't understand
            # OpAttr -- matches the live Evaluator's own resolution
            # (ADR 0206/LISS-0410), statically, with no runtime state.
            op_ast = resolve_static_operator(
                operators[name], unit=unit, operators=operators, objects=objects
            )
            nq = op_n_qubits(op_ast, operators, scalars)
            if nq == 0 or nq < 0:
                kind = "Fock" if nq == 0 else "grid"
                diags.append(
                    {
                        "code": "NON_UNITARY_TRANSFORM_ERROR",
                        "line": site.span.line,
                        "col": site.span.col,
                        "message": (
                            f"`apply`/`capply` cannot use {kind} Operator `{name}` "
                            f"as a gate unitary. Use `evolve … under {name}` for "
                            f"Schrödinger evolution, or a qubit unitary Operator."
                        ),
                    }
                )
                return
            if nq != n_wires:
                return
            mat = compile_hamiltonian(
                op_ast, env=operators, scalars=scalars, n_qubits=n_wires
            )
        else:
            mat = named_gate_matrix(name)
            if mat is None:
                return
            if n_wires != 1:
                return
        if not _is_unitary(mat):
            diags.append(
                {
                    "code": "NON_UNITARY_TRANSFORM_ERROR",
                    "line": site.span.line,
                    "col": site.span.col,
                    "message": (
                        f"`apply`/`capply` matrix for `{name}` is not unitary "
                        f"(U†U ≉ I). Use a unitary Operator or gate (Hadamard, Pauli, S, T)."
                    ),
                }
            )
    except (ValueError, TypeError, KeyError):
        return


def _check_hamiltonian_hermitian(
    name: str,
    op_ast: Any,
    operators: dict[str, Any],
    scalars: dict[str, float],
    objects: dict[str, Any],
    unit: CompilationUnit,
    diags: list[dict[str, Any]],
    site: Expr,
) -> None:
    try:
        # LISS-0411: same struct-field resolution as _check_apply_unitary.
        op_ast = resolve_static_operator(op_ast, unit=unit, operators=operators, objects=objects)
        nq = op_n_qubits(op_ast, operators, scalars)
        if nq == 0:
            mat = compile_hamiltonian(
                op_ast, env=operators, scalars=scalars, n_qubits=0, fock_dim=4
            )
        elif nq < 0:
            xs = [-3.0 + i * (6.0 / 16) for i in range(16)]
            mat = compile_hamiltonian(
                op_ast,
                env=operators,
                scalars=scalars,
                n_qubits=-1,
                grid_xs=xs,
            )
        else:
            mat = compile_hamiltonian(
                op_ast, env=operators, scalars=scalars, n_qubits=nq
            )
        if not _is_hermitian(mat):
            diags.append(
                {
                    "code": "NON_UNITARY_TRANSFORM_ERROR",
                    "line": site.span.line,
                    "col": site.span.col,
                    "message": (
                        f"Hamiltonian `{name}` is not Hermitian (H† ≉ H); "
                        f"`evolve under H` would not be unitary."
                    ),
                }
            )
    except (ValueError, TypeError, KeyError):
        return


def _is_unitary(m: list[list[complex]]) -> bool:
    n = len(m)
    prod = mat_mul(mat_dag(m), m)
    for i in range(n):
        for j in range(n):
            target = 1.0 if i == j else 0.0
            if abs(prod[i][j] - target) > _EPS:
                return False
    return True


def _is_hermitian(m: list[list[complex]]) -> bool:
    n = len(m)
    for i in range(n):
        for j in range(n):
            if abs(m[i][j] - m[j][i].conjugate()) > _EPS:
                return False
    return True


def _expr_is_quantum(
    expr: Expr, quantum: dict[str, bool], *, strict_mode: bool
) -> bool:
    ops = _STRICT_QUANTUM_OPS if strict_mode else _QUANTUM_OPS
    if isinstance(expr, KetLit):
        return True
    if isinstance(expr, KetSumBinder):
        return True
    if isinstance(expr, Coin):
        return False
    if isinstance(expr, Var):
        return quantum.get(expr.name, False)
    if isinstance(expr, Dirac):
        return _expr_is_quantum(expr.arg, quantum, strict_mode=strict_mode)
    if isinstance(expr, Inspect):
        return _expr_is_quantum(expr.expr, quantum, strict_mode=strict_mode)
    if isinstance(expr, UnaryNot):
        return _expr_is_quantum(expr.expr, quantum, strict_mode=strict_mode)
    if isinstance(expr, Call):
        op = _op_name(expr)
        if op in ops:
            return True
        if op == "expect":
            return False
        if op == "occupation":
            return False
        if not strict_mode and op in {"phase", "grover_diffuse"}:
            return True
        return any(
            _expr_is_quantum(a, quantum, strict_mode=strict_mode) for a in expr.args
        )
    if isinstance(expr, WhenExpr):
        return _expr_is_quantum(
            expr.ctrl, quantum, strict_mode=strict_mode
        ) or any(
            _expr_is_quantum(a.body, quantum, strict_mode=strict_mode)
            for a in expr.arms
        )
    if isinstance(expr, SuperposeExpr):
        # LISS-0375: `superpose (control) { ... }` is structurally
        # parallel to `WhenExpr` (SuperposeArm docstring) but was never
        # given the same coherent-lineage recognition here, so a state
        # bound via superpose was silently tracked as non-quantum.
        return _expr_is_quantum(
            expr.ctrl, quantum, strict_mode=strict_mode
        ) or any(
            _expr_is_quantum(a.body, quantum, strict_mode=strict_mode)
            for a in expr.arms
        )
    if isinstance(expr, BinOp):
        return _expr_is_quantum(
            expr.lhs, quantum, strict_mode=strict_mode
        ) or _expr_is_quantum(expr.rhs, quantum, strict_mode=strict_mode)
    if isinstance(expr, TensorExpr):
        return _expr_is_quantum(
            expr.left, quantum, strict_mode=strict_mode
        ) or _expr_is_quantum(expr.right, quantum, strict_mode=strict_mode)
    if isinstance(expr, EvolveExpr):
        if expr.hamiltonian is not None:
            return True
        return any(
            _expr_is_quantum(s, quantum, strict_mode=strict_mode) for s in expr.seeds
        )
    if isinstance(expr, TupleExpr):
        return any(
            _expr_is_quantum(it, quantum, strict_mode=strict_mode) for it in expr.items
        )
    if isinstance(expr, Pipe):
        return _expr_is_quantum(expr.rhs, quantum, strict_mode=strict_mode)
    if isinstance(expr, Attr):
        return _expr_is_quantum(expr.obj, quantum, strict_mode=strict_mode)
    if isinstance(expr, Lambda):
        return _expr_is_quantum(expr.body, quantum, strict_mode=strict_mode)
    return False


def _lambda_is_constant(fn: Expr) -> bool:
    if not isinstance(fn, Lambda):
        return False
    return not _mentions_name(fn.body, fn.param) and _is_closed_value(fn.body)


def _lambda_collapses_bits(fn: Expr) -> bool:
    """True if λ maps qubit labels 0 and 1 to the same closed value."""
    if not isinstance(fn, Lambda):
        return False
    try:
        v0 = _eval_lambda_bit(fn, 0)
        v1 = _eval_lambda_bit(fn, 1)
    except (TypeError, ValueError, ZeroDivisionError, KeyError):
        return False
    return v0 == v1


def _eval_lambda_bit(fn: Lambda, bit: int) -> Any:
    return _eval_closed_arith(fn.body, {fn.param: bit})


def _eval_closed_arith(expr: Expr, env: dict[str, Any]) -> Any:
    """Tiny closed evaluator for map-λ injectivity probes (Int/Float bits)."""
    if isinstance(expr, LitInt):
        return expr.value
    if isinstance(expr, LitFloat):
        return expr.value
    if isinstance(expr, LitBool):
        return expr.value
    if isinstance(expr, LitString):
        return expr.value
    if isinstance(expr, Dirac):
        return _eval_closed_arith(expr.arg, env)
    if isinstance(expr, Var):
        if expr.name not in env:
            raise KeyError(expr.name)
        return env[expr.name]
    if isinstance(expr, UnaryNot):
        return not bool(_eval_closed_arith(expr.expr, env))
    if isinstance(expr, BinOp):
        l = _eval_closed_arith(expr.lhs, env)
        r = _eval_closed_arith(expr.rhs, env)
        if expr.op == "+":
            return l + r
        if expr.op == "-":
            return l - r
        if expr.op == "*":
            return l * r
        if expr.op == "/":
            return l / r
        if expr.op == "==":
            return l == r
        if expr.op == "!=":
            return l != r
        if expr.op == "<":
            return l < r
        if expr.op == "<=":
            return l <= r
        if expr.op == ">":
            return l > r
        if expr.op == ">=":
            return l >= r
        raise ValueError(f"unsupported op {expr.op}")
    raise ValueError(f"unsupported expr {type(expr).__name__}")


def _mentions_name(expr: Expr, name: str) -> bool:
    if isinstance(expr, Var):
        return expr.name == name
    return any(_mentions_name(c, name) for c in _children(expr))


def _is_closed_value(expr: Expr) -> bool:
    return isinstance(expr, (LitInt, LitFloat, LitBool, LitString)) or (
        isinstance(expr, Dirac) and _is_closed_value(expr.arg)
    )


def _when_collapses(expr: WhenExpr) -> bool:
    """True if every arm body is the same closed literal (support collapse)."""
    vals: list[Any] = []
    for arm in expr.arms:
        body = arm.body
        if isinstance(body, Dirac):
            body = body.arg
        if not _is_closed_value(body):
            return False
        vals.append(_lit_value(body))
    return len(vals) >= 2 and len(set(vals)) == 1


def _is_numeric_lit(expr: Expr) -> bool:
    return isinstance(expr, (LitInt, LitFloat))


def _lit_value(expr: Expr) -> Any:
    if isinstance(expr, LitInt):
        return expr.value
    if isinstance(expr, LitFloat):
        return expr.value
    if isinstance(expr, LitBool):
        return expr.value
    if isinstance(expr, LitString):
        return expr.value
    if isinstance(expr, Dirac):
        return _lit_value(expr.arg)
    return None


def _op_name(expr: Call) -> str:
    cal = expr.callee
    if isinstance(cal, Var):
        return cal.name
    if isinstance(cal, Attr):
        return cal.name
    return ""


def _children(expr: Expr) -> Iterator[Expr]:
    if isinstance(expr, BinOp):
        yield expr.lhs
        yield expr.rhs
    elif isinstance(expr, Call):
        yield expr.callee
        yield from expr.args
    elif isinstance(expr, Attr):
        yield expr.obj
    elif isinstance(expr, Dirac):
        yield expr.arg
    elif isinstance(expr, Inspect):
        yield expr.expr
    elif isinstance(expr, UnaryNot):
        yield expr.expr
    elif isinstance(expr, Pipe):
        yield expr.lhs
        yield expr.rhs
    elif isinstance(expr, Lambda):
        yield expr.body
    elif isinstance(expr, TupleExpr):
        yield from expr.items
    elif isinstance(expr, TensorExpr):
        yield expr.left
        yield expr.right
    elif isinstance(expr, WhenExpr):
        yield expr.ctrl
        for arm in expr.arms:
            yield arm.body
    elif isinstance(expr, EvolveExpr):
        yield from expr.seeds
        if expr.duration is not None:
            yield expr.duration
        if expr.hamiltonian is not None:
            yield expr.hamiltonian
        if expr.body is not None:
            for lb in expr.body.lets:
                yield lb.expr
            yield expr.body.result
