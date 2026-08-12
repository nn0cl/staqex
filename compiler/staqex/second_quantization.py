"""Jordan-Wigner numerical mapping for typed second-quantized operators.

LISS-0032 / ADR 0093. Expands a `FermionOperator` symbolic expression (built
from `create(p)` / `annihilate(p)` atoms combined with `+`, `-`, `*`) into an
`OpExpr` Pauli-sum AST -- the same representation a hand-written `Operator`
expression (`X(0) * Z(1)`, ...) already produces -- so the existing SV
evaluator and QASM/Trotter lowering consume it unchanged.

Convention (normative, ADR 0093):

    a_p     = (prod_{k<p} Z_k) * (X_p + i Y_p) / 2
    a_p^dag = (prod_{k<p} Z_k) * (X_p - i Y_p) / 2

Scope: one-body and two-body fermionic terms (Bravyi-Kitaev, Boson, and Spin
mappings remain deferred). Correctness over performance: terms are expanded
by direct distribution (O(2^k) growth for a k-atom product) with no
term-count optimization, per the Adjudicator's explicit 2026-07-25 decision.
"""

from __future__ import annotations

from .ast_nodes import (
    BinOp,
    Call,
    Expr,
    LitInt,
    OpAttr,
    OpBin,
    OpCall,
    OpExpr,
    OpIndexed,
    OpLit,
    OpPauli,
    OpVar,
    Span,
    Var,
)

# Single-site Pauli multiplication: (phase, kind) = A * B (same table as
# runtime/sparse_pauli.py's _PAULI_MUL; duplicated to keep this module
# dependency-free of the runtime package).
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

# ADR 0195: relative fractions of the largest grouped coefficient present
# (see their scale-relative use in jordan_wigner_map below), not fixed
# absolute thresholds -- real-unit Hamiltonian coefficients (Joules) can be
# many orders of magnitude smaller than any plausible fixed epsilon.
_REAL_TOL = 1e-9
_ZERO_TOL = 1e-12

# A term is (complex coefficient, {qubit_index: pauli_letter}); the dict
# omits identity ("I") entries.
_Term = tuple[complex, dict]


class SecondQuantizationMappingError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _mul_term(a: _Term, b: _Term) -> _Term:
    coeff = a[0] * b[0]
    ops = dict(a[1])
    for q, letter in b[1].items():
        if q in ops:
            phase, result = _PAULI_MUL[(ops[q], letter)]
            coeff *= phase
            if result == "I":
                del ops[q]
            else:
                ops[q] = result
        else:
            ops[q] = letter
    return (coeff, ops)


def _mul_sums(s1: list[_Term], s2: list[_Term]) -> list[_Term]:
    return [_mul_term(a, b) for a in s1 for b in s2]


def _scale_sum(s: list[_Term], factor: complex) -> list[_Term]:
    return [(coeff * factor, ops) for coeff, ops in s]


def _parity_prefix(index: int) -> _Term:
    return (1 + 0j, {k: "Z" for k in range(index)})


def _create(index: int) -> list[_Term]:
    prefix = _parity_prefix(index)
    return [
        _mul_term(prefix, (0.5 + 0j, {index: "X"})),
        _mul_term(prefix, (-0.5j, {index: "Y"})),
    ]


def _annihilate(index: int) -> list[_Term]:
    prefix = _parity_prefix(index)
    return [
        _mul_term(prefix, (0.5 + 0j, {index: "X"})),
        _mul_term(prefix, (0.5j, {index: "Y"})),
    ]


def _orbital_index(expr, scalars: dict) -> int:
    if isinstance(expr, OpIndexed) and isinstance(expr.index, OpLit):
        return int(expr.index.value)
    # LISS-0368: a named integer local (`Int site = 0; create[site]`)
    # carries the identical static value as a literal index -- resolve it
    # through `scalars` the same way `_scalar_value` already resolves named
    # coefficients, instead of requiring the index to be written as a bare
    # literal.
    if isinstance(expr, OpIndexed) and isinstance(expr.index, OpVar):
        if expr.index.name in scalars:
            return int(scalars[expr.index.name])
    if (
        isinstance(expr, Call)
        and len(expr.args) == 1
        and isinstance(expr.args[0], LitInt)
    ):
        return expr.args[0].value
    if (
        isinstance(expr, Call)
        and len(expr.args) == 1
        and isinstance(expr.args[0], Var)
        and expr.args[0].name in scalars
    ):
        return int(scalars[expr.args[0].name])
    raise SecondQuantizationMappingError(
        "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
        "Jordan-Wigner mapping requires a static integer orbital index",
    )


def _resolve_static_attr_host(expr, objects: dict):
    """Resolve `OpVar`/nested `OpAttr` down to a host object with a
    `.fields` dict, supporting multi-level chains (`o.inner.c`)."""
    if isinstance(expr, OpVar):
        return objects.get(expr.name)
    if isinstance(expr, OpAttr):
        parent = _resolve_static_attr_host(expr.obj, objects)
        fields = getattr(parent, "fields", None)
        if not isinstance(fields, dict) or expr.name not in fields:
            return None
        return fields[expr.name]
    return None


def _static_op_attr_float(expr: OpAttr, objects: dict) -> float | None:
    """Resolve a struct-field coefficient (`weights.e0`) to a plain
    float, given a name -> object map whose values expose a `.fields`
    dict (matching a runtime `StructValue`/`ClassInstance`, or the
    `SimpleNamespace(fields=...)` shim `static_operator_resolution.py`
    builds for compile-time-only callers). Returns `None` (not a hard
    error) on any unresolvable shape -- `_scalar_value`'s caller already
    treats `None` as "not a pure scalar" and fails closed elsewhere.

    Deliberately duplicated rather than imported from
    `runtime.op_attr_elaboration` -- this module is kept dependency-free
    of the `runtime` package (see module docstring)."""
    host = _resolve_static_attr_host(expr.obj, objects)
    fields = getattr(host, "fields", None)
    if not isinstance(fields, dict) or expr.name not in fields:
        return None
    try:
        return float(fields[expr.name])
    except (TypeError, ValueError):
        return None


def _scalar_value(expr, scalars: dict, objects: dict | None = None) -> float | complex | None:
    """Evaluate `expr` as a plain classical scalar coefficient (a literal,
    a named Float/Energy/... binding, a struct-field coefficient, or a
    product/unary-minus of these), or return None when `expr` is not a
    pure scalar (e.g. it references `create`/`annihilate`) -- ADR 0195
    real-unit Hamiltonians attach a named scalar coefficient to each
    fermionic term, which this function lets `_expand` distribute
    instead of trying to expand as fermionic."""
    if isinstance(expr, OpLit):
        return expr.value
    if isinstance(expr, OpVar):
        if expr.name in scalars:
            return scalars[expr.name]
        return None
    if isinstance(expr, OpAttr):
        if objects is None:
            return None
        return _static_op_attr_float(expr, objects)
    if isinstance(expr, OpBin) and expr.op in {"*", "+", "-"}:
        lhs = _scalar_value(expr.lhs, scalars, objects)
        if lhs is None:
            return None
        rhs = _scalar_value(expr.rhs, scalars, objects)
        if rhs is None:
            return None
        if expr.op == "*":
            return lhs * rhs
        if expr.op == "+":
            return lhs + rhs
        return lhs - rhs
    return None


def _expand(expr, scalars: dict, objects: dict | None = None) -> list[_Term]:
    """Expand a FermionOperator symbolic expr into a raw (uncoalesced) Pauli
    sum with complex coefficients."""
    if isinstance(expr, OpIndexed) and isinstance(expr.base, OpVar):
        name = expr.base.name
        if name == "create":
            return _create(_orbital_index(expr, scalars))
        if name == "annihilate":
            return _annihilate(_orbital_index(expr, scalars))
        raise SecondQuantizationMappingError(
            "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
            f"`{name}` is not covered by the Jordan-Wigner mapping slice",
        )
    if isinstance(expr, Call) and isinstance(expr.callee, Var):
        name = expr.callee.name
        if name == "create":
            return _create(_orbital_index(expr, scalars))
        if name == "annihilate":
            return _annihilate(_orbital_index(expr, scalars))
        raise SecondQuantizationMappingError(
            "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
            f"`{name}` is not covered by the Jordan-Wigner mapping slice",
        )
    if isinstance(expr, OpCall):
        # LISS-0370: adjoint(x) of a fermionic sub-expression. Every term
        # `_expand` produces is (complex coefficient) * (Hermitian Pauli
        # tensor product) -- each single-qubit X/Y/Z/I factor is
        # self-adjoint, and different-site factors commute in this
        # dict-keyed representation, so (c * Op)^dagger = conj(c) * Op
        # and adjoint distributes over the term list. Verified
        # numerically: conjugating _create(i)'s terms exactly reproduces
        # _annihilate(i)'s terms.
        if expr.name == "adjoint" and len(expr.args) == 1:
            return [
                (coeff.conjugate(), ops)
                for coeff, ops in _expand(expr.args[0], scalars, objects)
            ]
        raise SecondQuantizationMappingError(
            "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
            f"`{expr.name}` is not covered by the Jordan-Wigner mapping slice",
        )
    if isinstance(expr, (OpBin, BinOp)):
        if expr.op == "*":
            lhs_scalar = _scalar_value(expr.lhs, scalars, objects)
            if lhs_scalar is not None:
                return _scale_sum(_expand(expr.rhs, scalars, objects), lhs_scalar)
            rhs_scalar = _scalar_value(expr.rhs, scalars, objects)
            if rhs_scalar is not None:
                return _scale_sum(_expand(expr.lhs, scalars, objects), rhs_scalar)
            lhs = _expand(expr.lhs, scalars, objects)
            rhs = _expand(expr.rhs, scalars, objects)
            return _mul_sums(lhs, rhs)
        if expr.op == "+":
            return _expand(expr.lhs, scalars, objects) + _expand(expr.rhs, scalars, objects)
        if expr.op == "-":
            return _expand(expr.lhs, scalars, objects) + _scale_sum(
                _expand(expr.rhs, scalars, objects), -1
            )
        raise SecondQuantizationMappingError(
            "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
            f"operator `{expr.op}` is not covered by the Jordan-Wigner mapping slice",
        )
    raise SecondQuantizationMappingError(
        "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
        f"`{type(expr).__name__}` is not covered by the Jordan-Wigner mapping slice",
    )


def _term_to_op_expr(ops: dict, span: Span):
    if not ops:
        return OpPauli(kind="I", site=None, span=span)
    node = None
    for site in sorted(ops):
        atom = OpPauli(kind=ops[site], site=site, span=span)
        node = atom if node is None else OpBin(op="*", lhs=node, rhs=atom, span=span)
    return node


def resolve_mapping_expr(
    expr: Expr,
    source_env: dict,
    scalars: dict | None = None,
    objects: dict | None = None,
) -> OpExpr | None:
    """If `expr` is `map(op, JordanWigner)` referencing a name already bound
    in `source_env` (a `FermionOperator` symbolic expr), return the mapped
    Pauli `OpExpr`. Returns `None` when `expr` is not a recognized mapping
    call so the caller keeps the bind symbolic instead.

    `scalars` (name -> real value) resolves named classical-scalar
    coefficients attached to fermionic terms (ADR 0195 real-unit
    Hamiltonians, e.g. `e0 * create[0] * annihilate[0]`); `objects`
    (LISS-0412) resolves struct-field coefficients the same way
    (`weights.e0 * create[0] * annihilate[0]`) -- omitted or
    unresolvable names/fields still fail closed inside
    `_expand`/`_scalar_value`.

    Shared by the SV evaluator (`runtime/evaluator.py`) and the QASM/Trotter
    lowering path (`backend/qasm/lower.py`) so both consume an identical
    mapped result from a single implementation.
    """
    if not (
        isinstance(expr, Call)
        and isinstance(expr.callee, Var)
        and expr.callee.name == "map"
        and len(expr.args) == 2
        and isinstance(expr.args[0], Var)
    ):
        return None
    source_expr = source_env.get(expr.args[0].name)
    if source_expr is None:
        return None
    mapped_expr, _qubit_count = jordan_wigner_map(
        source_expr, span=expr.span, scalars=scalars, objects=objects
    )
    return mapped_expr


def jordan_wigner_map(
    expr, *, span: Span, scalars: dict | None = None, objects: dict | None = None
) -> tuple[object, int]:
    """Expand a FermionOperator expr into an (OpExpr, qubit_count) pair.

    The OpExpr is built from real OpLit coefficients and OpPauli/OpBin
    nodes -- the same shape the parser produces for a hand-written Operator
    expression -- so it is consumable by the existing SV evaluator and the
    existing QASM/Trotter lowering path without any further change there.
    """
    raw_terms = _expand(expr, scalars or {}, objects)

    grouped: dict[tuple, complex] = {}
    for coeff, ops in raw_terms:
        key = tuple(sorted(ops.items()))
        grouped[key] = grouped.get(key, 0j) + coeff

    max_index = -1
    for key in grouped:
        for site, _letter in key:
            max_index = max(max_index, site)
    qubit_count = max(max_index + 1, 1)

    # ADR 0195: real-unit coefficients (Joules) are routinely far below any
    # fixed absolute epsilon (same bug class as sparse_pauli.py::_coalesce,
    # LISS-0336) -- scale both the zero-drop and the non-Hermitian-residual
    # thresholds to the largest coefficient present so genuine
    # floating-point noise is still caught without zeroing real
    # small-magnitude SI values.
    scale = max((abs(c) for c in grouped.values()), default=0.0)
    zero_tol = scale * _ZERO_TOL
    real_tol = scale * _REAL_TOL

    result = None
    for key, coeff in grouped.items():
        if abs(coeff) <= zero_tol:
            continue
        if abs(coeff.imag) > real_tol:
            raise SecondQuantizationMappingError(
                "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED",
                "Jordan-Wigner mapping result is not expressible as a real "
                f"Pauli sum (non-Hermitian residual {coeff!r} on term {dict(key)!r}); "
                "the source fermionic expression must be Hermitian",
            )
        term_node = _term_to_op_expr(dict(key), span)
        real_coeff = coeff.real
        scaled = (
            term_node
            if real_coeff == 1.0
            else OpBin(op="*", lhs=OpLit(value=real_coeff, span=span), rhs=term_node, span=span)
        )
        result = scaled if result is None else OpBin(op="+", lhs=result, rhs=scaled, span=span)

    if result is None:
        result = OpLit(value=0.0, span=span)
    return result, qubit_count
