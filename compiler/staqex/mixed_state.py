"""Mixed-state contract extraction for the first LISS-0011 slice."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt

from .ast_nodes import (
    BinOp,
    Call,
    CompilationUnit,
    FunDecl,
    KetLit,
    ListExpr,
    LitFloat,
    LitInt,
    OpBin,
    OpIndexed,
    OpLit,
    OpPauli,
    OpPow,
    StateBind,
    TupleExpr,
    Var,
)
from .runtime.numeric_policy import PHYSICAL_TOLERANCE


TRACE_EPSILON = PHYSICAL_TOLERANCE
POSITIVITY_EPSILON = PHYSICAL_TOLERANCE
KRAUS_EPSILON = PHYSICAL_TOLERANCE


@dataclass(frozen=True, slots=True)
class MixedStateContract:
    name: str
    kind: str
    operation: str
    domain: str
    input_domain: str | None = None
    output_domain: str | None = None
    sealed: bool = True


def resolve_mixed_state_contracts(
    unit: CompilationUnit,
) -> tuple[dict[str, MixedStateContract], list[dict]]:
    if unit.main is None:
        return {}, []
    contracts: dict[str, MixedStateContract] = {}
    diagnostics: list[dict] = []
    kinds: dict[str, str] = {}
    operator_names: set[str] = set()
    operator_exprs: dict[str, object] = {}
    channel_names: set[str] = set()
    # Actual constructed dimension of each DensityState local, derived from
    # its RawMatrix literal (LISS-0011: the type parameter, e.g. `Qubit`, is
    # a domain label only and does not itself encode a qubit count).
    density_dims: dict[str, int] = {}
    scalars: dict[str, float] = {}
    for statement in unit.main.body.stmts:
        if not isinstance(statement, StateBind) or statement.ty is None:
            continue
        if len(statement.names) != 1:
            continue
        if statement.ty.name == "Operator":
            operator_names.add(statement.names[0])
            operator_exprs[statement.names[0]] = statement.expr
        elif statement.ty.name == "Channel":
            channel_names.add(statement.names[0])
        elif statement.ty.name in {"Float", "Int"}:
            value = _number(statement.expr, scalars)
            if value is not None:
                scalars[statement.names[0]] = value
    for statement in unit.main.body.stmts:
        if not isinstance(statement, StateBind) or statement.ty is None:
            continue
        name = statement.names[0] if len(statement.names) == 1 else ""
        if not name:
            continue
        type_name = statement.ty.name
        if type_name == "Channel":
            args = statement.ty.args
            input_domain = args[0].name if len(args) > 0 else None
            output_domain = args[1].name if len(args) > 1 else None
            contracts[name] = MixedStateContract(
                name=name,
                kind="Channel",
                operation=_call_name(statement.expr) or "channel",
                domain="Channel",
                input_domain=input_domain,
                output_domain=output_domain,
            )
            kinds[name] = "Channel"
            kraus_error = None
            if isinstance(statement.expr, Call) and _call_name(statement.expr) == "KrausChannel":
                kraus_error = _kraus_error(statement.expr)
            if kraus_error is not None:
                diagnostics.append(
                    {
                        "code": "INCOMPLETE_KRAUS_CHANNEL",
                        "line": statement.span.line,
                        "col": statement.span.col,
                        "message": kraus_error,
                    }
                )
            continue
        if type_name != "DensityState":
            kinds[name] = type_name
            continue
        operation = _call_name(statement.expr) or "density_state"
        domain = statement.ty.args[0].name if statement.ty.args else "Unknown"
        if operation == "DensityState":
            validity_error = _density_constructor_error(statement.expr, scalars)
            if validity_error is not None:
                diagnostics.append(
                    {
                        "code": "MALFORMED_DENSITY_STATE",
                        "line": statement.span.line,
                        "col": statement.span.col,
                        "message": validity_error,
                    }
                )
            dim = _raw_matrix_dimension(statement.expr, scalars)
            if dim is not None:
                density_dims[name] = dim
        if operation == "lindblad" and isinstance(statement.expr, Call):
            source_name = (
                statement.expr.args[0].name
                if statement.expr.args and isinstance(statement.expr.args[0], Var)
                else None
            )
            expected = (
                density_dims.get(source_name) if source_name is not None else None
            )
            jump_code, jump_error = _lindblad_jump_error(
                statement.expr,
                source_domain=domain,
                expected=expected,
                operator_names=operator_names,
                operator_exprs=operator_exprs,
                channel_names=channel_names,
            )
            if jump_error is not None:
                diagnostics.append(
                    {
                        "code": jump_code,
                        "line": statement.span.line,
                        "col": statement.span.col,
                        "message": jump_error,
                    }
                )
        if operation == "apply" and isinstance(statement.expr, Call):
            if len(statement.expr.args) > 1 and _apply_arg_is_state(
                statement.expr.args[1], kinds, unit
            ):
                diagnostics.append(
                    {
                        "code": "MIXED_STATE_TYPE_ERROR",
                        "line": statement.span.line,
                        "col": statement.span.col,
                        "message": "Channel application requires DensityState; use pure_to_density explicitly",
                    }
                )
        contracts[name] = MixedStateContract(
            name=name,
            kind="DensityState",
            operation=operation,
            domain=domain,
        )
        kinds[name] = "DensityState"
    return contracts, diagnostics


def _apply_arg_is_state(
    expr: object,
    kinds: dict[str, str],
    unit: CompilationUnit,
) -> bool:
    """True when an apply() source is a State-kind value (LISS-0379).

    Previously only bare ``Var`` names in ``kinds`` were checked, so
    ``apply(ch, id(psi))`` silently skipped ``MIXED_STATE_TYPE_ERROR``.
    """
    if isinstance(expr, Var):
        return kinds.get(expr.name) == "State"
    if not isinstance(expr, Call) or not isinstance(expr.callee, Var):
        return False
    for decl in unit.decls:
        if not isinstance(decl, FunDecl) or decl.name != expr.callee.name:
            continue
        return_type = decl.return_type
        return return_type is not None and return_type.name == "State"
    return False


def _call_name(expr: object) -> str | None:
    if isinstance(expr, Call) and isinstance(expr.callee, Var):
        return expr.callee.name
    return None


def _density_constructor_error(
    expr: Call, scalars: dict[str, float] | None = None
) -> str | None:
    if len(expr.args) != 1 or not isinstance(expr.args[0], Call):
        return "DensityState requires one Ensemble or RawMatrix input"
    source = expr.args[0]
    name = _call_name(source)
    if name == "Ensemble":
        return _validate_ensemble(source, scalars)
    if name == "RawMatrix":
        return _validate_raw_matrix(source, scalars)
    return "DensityState input must be Ensemble or RawMatrix"


def _validate_ensemble(
    expr: Call, scalars: dict[str, float] | None = None
) -> str | None:
    if len(expr.args) != 1 or not isinstance(expr.args[0], ListExpr):
        return "Ensemble requires a finite list of weighted states"
    weights: list[float] = []
    for item in expr.args[0].items:
        if not isinstance(item, TupleExpr) or len(item.items) != 2:
            return "Ensemble entries must be `(weight, state)` pairs"
        weight = _number(item.items[0], scalars)
        if weight is None or weight < -TRACE_EPSILON:
            return "Ensemble weights must be finite and non-negative"
        if not isinstance(item.items[1], (KetLit, Var)):
            return "Ensemble states must be explicit finite state values"
        weights.append(weight)
    if not weights or abs(sum(weights) - 1.0) > TRACE_EPSILON:
        return "DensityState trace must equal one within 1e-12"
    return None


def _validate_raw_matrix(
    expr: Call, scalars: dict[str, float] | None = None
) -> str | None:
    if len(expr.args) != 1 or not isinstance(expr.args[0], ListExpr):
        return "RawMatrix requires a finite square numeric matrix"
    rows = expr.args[0].items
    matrix: list[list[float]] = []
    for row in rows:
        if not isinstance(row, ListExpr):
            return "RawMatrix requires a finite square numeric matrix"
        values = [_number(item, scalars) for item in row.items]
        if any(value is None for value in values):
            return "RawMatrix entries must be finite numeric values"
        matrix.append([value for value in values if value is not None])
    if not matrix or any(len(row) != len(matrix) for row in matrix):
        return "RawMatrix must be square"
    if any(not isfinite(value) for row in matrix for value in row):
        return "RawMatrix entries must be finite numeric values"
    trace = sum(matrix[index][index] for index in range(len(matrix)))
    if abs(trace - 1.0) > TRACE_EPSILON:
        return "DensityState trace must equal one within 1e-12"
    if len(matrix) == 2:
        if abs(matrix[0][1] - matrix[1][0]) > POSITIVITY_EPSILON:
            return "RawMatrix must be Hermitian"
        minimum = (
            matrix[0][0]
            + matrix[1][1]
            - sqrt(
                (matrix[0][0] - matrix[1][1]) ** 2
                + 4.0 * matrix[0][1] * matrix[0][1]
            )
        ) / 2.0
        if minimum < -POSITIVITY_EPSILON:
            return "DensityState must be positive semidefinite"
    return None


def _number(
    expr: object, scalars: dict[str, float] | None = None
) -> float | None:
    """Resolve a classical numeric leaf for mixed-state constructors.

    LISS-0378: previously only LitInt/LitFloat were accepted, so
    ``1.0 * 1.0`` and a named ``Float w`` were spuriously rejected.
    """
    if isinstance(expr, LitInt):
        return float(expr.value)
    if isinstance(expr, LitFloat):
        return float(expr.value)
    if isinstance(expr, Var) and scalars is not None:
        return scalars.get(expr.name)
    if isinstance(expr, BinOp):
        left = _number(expr.lhs, scalars)
        right = _number(expr.rhs, scalars)
        if left is None or right is None:
            return None
        if expr.op == "+":
            return left + right
        if expr.op == "-":
            return left - right
        if expr.op == "*":
            return left * right
        if expr.op == "/":
            if right == 0.0:
                return None
            return left / right
    return None


def _kraus_error(expr: Call) -> str | None:
    if len(expr.args) != 1 or not isinstance(expr.args[0], ListExpr):
        return "KrausChannel requires a finite numeric operator list"
    matrices: list[list[list[float]]] = []
    for item in expr.args[0].items:
        matrix = _matrix_values(item)
        if matrix is None:
            return "KrausChannel requires explicit finite numeric matrices"
        matrices.append(matrix)
    if not matrices:
        return "KrausChannel requires at least one operator"
    size = len(matrices[0])
    if any(len(matrix) != size for matrix in matrices):
        return "Kraus operators must have matching dimensions"
    total = [[0.0 for _ in range(size)] for _ in range(size)]
    for matrix in matrices:
        if any(len(row) != size for row in matrix):
            return "Kraus operators must be square"
        for row in range(size):
            for col in range(size):
                total[row][col] += sum(
                    matrix[index][row] * matrix[index][col]
                    for index in range(size)
                )
    for row in range(size):
        for col in range(size):
            expected = 1.0 if row == col else 0.0
            if abs(total[row][col] - expected) > KRAUS_EPSILON:
                return "Kraus operators must satisfy sum(K_i† K_i) = I"
    return None


def _lindblad_jump_error(
    expr: Call,
    *,
    source_domain: str,
    expected: int | None,
    operator_names: set[str],
    operator_exprs: dict[str, object],
    channel_names: set[str],
) -> tuple[str | None, str | None]:
    if len(expr.args) != 4:
        return "INVALID_LINDBLAD_JUMP_SET", "lindblad requires source, H, jumps, and time"
    jumps = expr.args[2]
    if isinstance(jumps, ListExpr):
        if not jumps.items:
            return None, None
        return "INVALID_LINDBLAD_JUMP_SET", (
            "non-empty Lindblad jumps must use JumpSet([...])"
        )
    if not isinstance(jumps, Call) or _call_name(jumps) != "JumpSet":
        return None, None
    if len(jumps.args) != 1 or not isinstance(jumps.args[0], ListExpr):
        return "INVALID_LINDBLAD_JUMP_SET", "JumpSet requires a finite list"
    for item in jumps.args[0].items:
        if isinstance(item, Var):
            if item.name in channel_names:
                return "INVALID_LINDBLAD_JUMP_SET", (
                    "Channel values are not Lindblad jump operators"
                )
            if item.name not in operator_names:
                return "SYMBOLIC_JUMP_LOWERING_REQUIRED", (
                    f"jump `{item.name}` must resolve to an Operator"
                )
            if expected is not None and _operator_exceeds_dimension(
                item.name, operator_exprs, expected
            ):
                return "LINDBLAD_JUMP_DIMENSION_ERROR", (
                    f"jump matrix dimension must match {source_domain} ({expected})"
                )
            continue
        if not isinstance(item, Call) or _call_name(item) != "RawMatrix":
            return "INVALID_LINDBLAD_JUMP_SET", (
                "JumpSet entries must be RawMatrix values or bound Operators"
            )
        matrix = _matrix_values(item.args[0]) if len(item.args) == 1 else None
        if matrix is None:
            return "INVALID_LINDBLAD_JUMP_SET", (
                "JumpSet entries must be finite square numeric matrices"
            )
        if expected is not None and len(matrix) != expected:
            return "LINDBLAD_JUMP_DIMENSION_ERROR", (
                f"jump matrix dimension must match {source_domain} ({expected})"
            )
    return None, None


def _raw_matrix_dimension(
    expr: Call, scalars: dict[str, float] | None = None
) -> int | None:
    """Actual constructed dimension of a `DensityState(RawMatrix([...]))`
    bind, or None when the input is an `Ensemble` or otherwise not
    statically sized (LISS-0011)."""
    if len(expr.args) != 1 or not isinstance(expr.args[0], Call):
        return None
    source = expr.args[0]
    if _call_name(source) != "RawMatrix":
        return None
    matrix = (
        _matrix_values(source.args[0], scalars) if len(source.args) == 1 else None
    )
    return len(matrix) if matrix is not None else None


def _operator_exceeds_dimension(
    name: str, operator_exprs: dict[str, object], expected: int
) -> bool:
    expr = operator_exprs[name]
    max_site = expected.bit_length() - 2  # expected = 2**n_qubits -> max valid site n-1

    def walk(node: object) -> bool:
        if isinstance(node, OpPauli):
            return node.site is not None and node.site > max_site
        if isinstance(node, OpIndexed):
            return (
                isinstance(node.base, OpPauli)
                and isinstance(node.index, OpLit)
                and int(node.index.value) > max_site
            )
        if isinstance(node, OpBin):
            return walk(node.lhs) or walk(node.rhs)
        if isinstance(node, OpPow):
            return walk(node.base)
        return False

    return walk(expr)


def _matrix_values(
    expr: object, scalars: dict[str, float] | None = None
) -> list[list[float]] | None:
    if not isinstance(expr, ListExpr):
        return None
    matrix: list[list[float]] = []
    for row in expr.items:
        if not isinstance(row, ListExpr):
            return None
        values = [_number(item, scalars) for item in row.items]
        if any(value is None for value in values):
            return None
        matrix.append([value for value in values if value is not None])
    if not matrix or any(len(row) != len(matrix) for row in matrix):
        return None
    return matrix
