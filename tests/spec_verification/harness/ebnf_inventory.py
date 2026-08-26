"""Compare the shipped grammar inventory against selected lexer/parser evidence."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class InventoryReport:
    missing_from_grammar: tuple[str, ...]
    extra_in_grammar: tuple[str, ...] = ()


_GRAMMAR = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "specs"
    / "grammar"
    / "staqex.ebnf"
)
_QUOTED = re.compile(r'"([^"\n]+)"')
_MODERN_KEYWORDS = frozenset({"namespace", "enum", "struct", "dynamic"})
_SCIENTIFIC_SCOPE_HEADS = frozenset(
    {"theory", "experiment", "workflow", "execution", "report", "system"}
)
_CONTEXTUAL_VERSIONING = frozenset({"until", "max", "pub", "in"})
_ASCII_QUANTUM_TOKENS = frozenset({"*|*", "<", ">"})
_NUMERIC_SEPARATOR_MARKERS = frozenset({"_"})

_REQUIRED_INVENTORY = frozenset().union(
    _MODERN_KEYWORDS,
    _SCIENTIFIC_SCOPE_HEADS,
    _CONTEXTUAL_VERSIONING,
    _ASCII_QUANTUM_TOKENS,
    _NUMERIC_SEPARATOR_MARKERS,
)


def compare_grammar_to_shipping(path: Path | None = None) -> InventoryReport:
    grammar = (path or _GRAMMAR).read_text(encoding="utf-8")
    present = set(_QUOTED.findall(grammar))
    missing = tuple(sorted(item for item in _REQUIRED_INVENTORY if item not in present))
    return InventoryReport(missing_from_grammar=missing)
