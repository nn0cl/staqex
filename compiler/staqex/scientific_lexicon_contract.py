"""Read-only scientific lexicon contract inspection.

The current source policy is ASCII-only for quantum notation.  This module
records the accepted display aliases and provenance without changing lexer
tokens or introducing a second semantic operation.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType

from .ast_nodes import BlockExpr, Dirac, EvolveExpr, KetLit, StateBind, Vacuum
from .pipeline import compile_source


@dataclass(frozen=True, slots=True)
class LexiconBinding:
    canonical_id: str
    display_symbol: str | None
    token_class: str
    context: str
    written_form: str
    semantic_operation: str | None


@dataclass(frozen=True, slots=True)
class LexiconOperation:
    canonical_id: str
    written_form: str
    display_form: str
    token_class: str
    semantic_operation: str


@dataclass(frozen=True, slots=True)
class LexiconInspection:
    source_id: str
    contract_version: str
    bindings: dict[str, LexiconBinding]
    operations: tuple[LexiconOperation, ...]
    shadowing_policy: str
    scoped_bindings: tuple["ScopedLexiconBinding", ...] = ()


@dataclass(frozen=True, slots=True)
class ScopedLexiconBinding:
    """Scientific alias metadata after lexical resolution."""

    name: str
    context: str
    scope_depth: int
    binding_id: str
    declaration_span: tuple[int, int]


_CONTRACT_VERSION = "scientific-lexicon-v1"
_DISPLAY_SYMBOLS = MappingProxyType({"psi": "ψ", "phi": "φ", "rho": "ρ"})
_SCIENTIFIC_NAMES = frozenset(_DISPLAY_SYMBOLS)
_COMMUTATOR = re.compile(r"\bcm\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)")
_SCIENTIFIC_CONTEXT = "quantum_state"
_ORDINARY_CONTEXT = "classical_scalar"
_LEXICON_FATAL_CODES = frozenset(
    {"PARSE_ERROR", "LEX_ERROR", "TYPE_ERROR", "TYPE_MISMATCH", "TYPE_NOT_STATE"}
)


def _binding_for_statement(statement: StateBind) -> LexiconBinding:
    name = statement.name
    if name in _SCIENTIFIC_NAMES:
        return LexiconBinding(
            canonical_id=name,
            display_symbol=_DISPLAY_SYMBOLS[name],
            token_class="scientific_identifier",
            context=_SCIENTIFIC_CONTEXT,
            written_form=name,
            semantic_operation=None,
        )
    return LexiconBinding(
        canonical_id=name,
        display_symbol=None,
        token_class="ordinary_identifier",
        context=_ORDINARY_CONTEXT,
        written_form=name,
        semantic_operation=None,
    )


def _source_without_comments(source: str) -> str:
    return re.sub(r"//[^\n]*", "", source)


def _commutator_operation(source: str) -> tuple[LexiconOperation, ...]:
    return tuple(
        LexiconOperation(
            canonical_id="commutator",
            written_form="cm",
            display_form=f"[{match.group(1)}, {match.group(2)}]",
            token_class="scientific_operator_alias",
            semantic_operation="commutator",
        )
        for match in _COMMUTATOR.finditer(_source_without_comments(source))
    )


def _scoped_bindings(main: object, source_id: str) -> tuple[ScopedLexiconBinding, ...]:
    result: list[ScopedLexiconBinding] = []

    def add(name: str, context: str, depth: int, span: object) -> None:
        if name not in _SCIENTIFIC_NAMES:
            return
        line = int(getattr(span, "line", 0))
        col = int(getattr(span, "col", 0))
        result.append(
            ScopedLexiconBinding(
                name=name,
                context=context,
                scope_depth=depth,
                binding_id=f"{source_id}:{line}:{col}:{depth}:{name}",
                declaration_span=(line, col),
            )
        )

    def walk_expr(expr: object, depth: int) -> None:
        if isinstance(expr, BlockExpr):
            for let in expr.lets:
                context = (
                    _SCIENTIFIC_CONTEXT
                    if isinstance(let.expr, (KetLit, Dirac, Vacuum))
                    else _ORDINARY_CONTEXT
                )
                add(let.name, context, depth + 1, let.span)
                walk_expr(let.expr, depth + 1)
            walk_expr(expr.result, depth + 1)
        elif isinstance(expr, EvolveExpr) and expr.body is not None:
            for let in expr.body.lets:
                add(let.name, _SCIENTIFIC_CONTEXT, depth + 1, let.span)
                walk_expr(let.expr, depth + 1)
            walk_expr(expr.body.result, depth + 1)

    statements = getattr(getattr(main, "body", None), "stmts", ())
    for statement in statements:
        if isinstance(statement, StateBind):
            add(statement.name, _SCIENTIFIC_CONTEXT, 0, statement.span)
            walk_expr(statement.expr, 0)
    return tuple(result)


def inspect_source(source: str, *, source_id: str) -> LexiconInspection:
    """Inspect accepted lexicon metadata while preserving source provenance."""

    code = _source_without_comments(source)
    if any(ord(character) > 127 for character in code):
        raise ValueError(
            "unsupported scientific spelling; use the canonical ASCII spelling"
        )

    compiled = compile_source(source)
    # Lexicon inspection is a source/provenance view.  Runtime readiness and
    # linearity diagnostics are intentionally allowed here; syntax and basic
    # type failures must still prevent metadata from being fabricated.
    if any(
        diagnostic.get("code") in _LEXICON_FATAL_CODES
        for diagnostic in compiled.diagnostics
    ):
        raise ValueError("unsupported scientific spelling")
    unit = compiled.unit
    main = getattr(unit, "main", None)
    statements = getattr(getattr(main, "body", None), "stmts", ())
    bindings = {
        statement.name: _binding_for_statement(statement)
        for statement in statements
        if isinstance(statement, StateBind)
    }
    operations = _commutator_operation(source)
    if not bindings and not operations:
        raise ValueError("unsupported scientific spelling")
    return LexiconInspection(
        source_id=source_id,
        contract_version=_CONTRACT_VERSION,
        bindings=bindings,
        operations=operations,
        shadowing_policy="nearest_typed_declaration",
        scoped_bindings=_scoped_bindings(main, source_id),
    )
