"""Staqex token kinds (ADR 0035)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenKind(Enum):
    # Active keywords
    CLASS = auto()
    INTERFACE = auto()
    IMPL = auto()
    PACKAGE = auto()
    IMPORT = auto()
    NAMESPACE = auto()
    ENUM = auto()
    STRUCT = auto()
    FUN = auto()
    STATE = auto()
    LET = auto()
    WHEN = auto()
    SUPERPOSE = auto()
    COIN = auto()
    DIRAC = auto()
    VACUUM = auto()
    EVOLVE = auto()
    MEASURE = auto()
    SNAPSHOT = auto()
    INSPECT = auto()
    THIS = auto()
    VAL = auto()
    VAR = auto()
    MODULE = auto()
    EXPORTS = auto()
    REQUIRES = auto()
    PROTECTED = auto()
    PRIVATE = auto()
    RETURN = auto()
    FOREACH = auto()
    DYNAMIC = auto()

    # Contextual (parser soft keywords)
    ELSE = auto()
    PUBLIC = auto()
    TRUE = auto()
    FALSE = auto()
    FOR = auto()
    TO = auto()
    TIMES = auto()
    UNDER = auto()
    IN = auto()
    UNTIL = auto()
    MAX = auto()
    ONTO = auto()

    # Forbidden (hard error — still emitted so diagnostics have spans)
    FORBIDDEN = auto()

    # Retired (linter / fix-it)
    RETIRED = auto()

    # Literals / idents / ops
    IDENT = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()

    PIPE_OP = auto()  # |>
    TENSOR_OP = auto()  # *|* (ASCII source form)
    CARET = auto()  # ^
    KET = auto()  # |0>, |+>, |01>, …
    BRA = auto()  # <0| (ASCII source form)
    DAGGER = auto()  # postfix adjoint token (reserved for future ASCII form)

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()
    EQEQ = auto()
    NEQ = auto()
    AND = auto()  # && — binder where guards only (LISS-0141)
    OR = auto()  # || — binder where guards only (LISS-0145)
    BANG = auto()  # !  (open-control polarity; != is NEQ)
    LT = auto()
    LE = auto()
    GT = auto()
    GE = auto()
    ARROW = auto()  # ->
    FAT_ARROW = auto()  # => — match arms (ADR 0197 / LISS-0382)

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    DOT = auto()
    RANGE = auto()  # .. (inclusive finite range)
    COLON = auto()
    SEMI = auto()

    EOF = auto()
    ERROR = auto()


ACTIVE: dict[str, TokenKind] = {
    "class": TokenKind.CLASS,
    "interface": TokenKind.INTERFACE,
    "impl": TokenKind.IMPL,
    "package": TokenKind.PACKAGE,
    "import": TokenKind.IMPORT,
    "namespace": TokenKind.NAMESPACE,
    "enum": TokenKind.ENUM,
    "struct": TokenKind.STRUCT,
    "fn": TokenKind.FUN,
    "return": TokenKind.RETURN,
    "forEach": TokenKind.FOREACH,
    "dynamic": TokenKind.DYNAMIC,
    "state": TokenKind.STATE,
    "let": TokenKind.LET,
    "mix": TokenKind.WHEN,
    "superpose": TokenKind.SUPERPOSE,
    "coin": TokenKind.COIN,
    "dirac": TokenKind.DIRAC,
    "vacuum": TokenKind.VACUUM,
    "evolve": TokenKind.EVOLVE,
    "measure": TokenKind.MEASURE,
    "snapshot": TokenKind.SNAPSHOT,
    "inspect": TokenKind.INSPECT,
    "this": TokenKind.THIS,
    "val": TokenKind.VAL,
    "var": TokenKind.VAR,
    "module": TokenKind.MODULE,
    "exports": TokenKind.EXPORTS,
    "requires": TokenKind.REQUIRES,
    "private": TokenKind.PRIVATE,
}

CONTEXTUAL: dict[str, TokenKind] = {
    "else": TokenKind.ELSE,
    "pub": TokenKind.PUBLIC,
    "true": TokenKind.TRUE,
    "false": TokenKind.FALSE,
    "to": TokenKind.TO,
    "times": TokenKind.TIMES,
    "for": TokenKind.FOR,  # evolve (…) for dt {…} | evolve psi under H for t
    "under": TokenKind.UNDER,
    "in": TokenKind.IN,
    "until": TokenKind.UNTIL,
    "max": TokenKind.MAX,
    "onto": TokenKind.ONTO,
}

FORBIDDEN: set[str] = {
    "if",
    "switch",
    "while",
    # `for` is contextual inside evolve; bare C-style for-loops still fail to parse
    "break",
    "new",
    "null",
    "try",
    "catch",
    "throw",
    "Thread",
    "async",
    "await",
    "protected",
}

RETIRED: dict[str, str] = {
    "observe": "measure",
    "span": "mix",
    "when": "mix",
    "fun": "fn",
    "public": "pub",
    "trait": "interface",
}

FORBIDDEN_MESSAGES: dict[str, str] = {
    "if": (
        "NON_UNITARY_DECOHERENCE_ERROR: 'if' destroys unitary evolution on "
        "superpositions. Apply a linear operator (H, CNOT, e^{-iHt}, …) or "
        "perform an explicit `measure`; do not branch on an unmeasured quantum wire."
    ),
    "switch": (
        "NON_UNITARY_DECOHERENCE_ERROR: 'switch' is classical control flow. "
        "Use a linear operator or explicit `measure`."
    ),
    "while": (
        "NON_UNITARY_DECOHERENCE_ERROR: 'while' is classical iteration. "
        "Use `evolve … under H for t` or `evolve … times N {…}` for closed dynamics."
    ),
    "break": "Syntax Error: 'break' is forbidden; early exit tears the joint.",
    "return": "Syntax Error: 'return' is forbidden; use block result / evolve.",
    "new": "Syntax Error: Construct with Foo(args); 'new' is forbidden.",
    "null": "Syntax Error: Use Result / mix basis labels / empty(); 'null' is forbidden.",
    "try": "Syntax Error: Exceptions are forbidden; use Result + mix.",
    "catch": "Syntax Error: Exceptions are forbidden; use Result + mix.",
    "throw": "Syntax Error: Exceptions are forbidden; use Result + mix.",
    "Thread": "Syntax Error: Concurrency is mix / joint product; threads are forbidden.",
    "async": "Syntax Error: Concurrency is mix / joint product; async is forbidden.",
    "await": "Syntax Error: Concurrency is mix / joint product; await is forbidden.",
    "protected": (
        "FORBIDDEN_CONSTRUCT: `protected` requires inheritance; Staqex uses "
        "composition + `pub` / leading `_` instead (ADR 0058)."
    ),
}


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    lexeme: str
    line: int
    col: int
    literal: Any = None
    meta: dict[str, str] | None = None  # e.g. replacement for RETIRED
