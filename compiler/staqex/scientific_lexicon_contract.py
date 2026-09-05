"""Read-only scientific lexicon contract inspection.

The current source policy is ASCII-only for quantum notation.  This module
records the accepted display aliases and provenance without changing lexer
tokens or introducing a second semantic operation.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from types import MappingProxyType

from .ast_nodes import StateBind
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


_CONTRACT_VERSION = "scientific-lexicon-v1"
_DISPLAY_SYMBOLS = MappingProxyType({"psi": "ψ", "phi": "φ", "rho": "ρ"})
_SCIENTIFIC_NAMES = frozenset(_DISPLAY_SYMBOLS)
_COMMUTATOR = re.compile(r"\bcm\s*\(")
_SCIENTIFIC_CONTEXT = "quantum_state"
_ORDINARY_CONTEXT = "classical_scalar"


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


def _commutator_operation(source: str) -> tuple[LexiconOperation, ...]:
    if _COMMUTATOR.search(source) is None:
        return ()
    return (
        LexiconOperation(
            canonical_id="commutator",
            written_form="cm",
            display_form="[X, Y]",
            token_class="scientific_operator_alias",
            semantic_operation="commutator",
        ),
    )


def inspect_source(source: str, *, source_id: str) -> LexiconInspection:
    """Inspect accepted lexicon metadata while preserving source provenance."""

    if any(ord(character) > 127 for character in source):
        raise ValueError(
            "unsupported scientific spelling; use the canonical ASCII spelling"
        )

    compiled = compile_source(source)
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
    )
