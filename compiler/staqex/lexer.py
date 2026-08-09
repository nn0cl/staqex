"""Staqex Lexer (ADR 0035 / qpex-token-specification.md)."""

from __future__ import annotations

from .tokens import (
    ACTIVE,
    CONTEXTUAL,
    FORBIDDEN,
    FORBIDDEN_MESSAGES,
    RETIRED,
    Token,
    TokenKind,
)
from .kernel_literals import DIRAC_LABEL_EXTRAS as _DIRAC_LABEL_EXTRAS

_KET_CLOSE_CHARS = frozenset({">"})


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.i = 0
        self.line = 1
        self.col = 1
        self.tokens: list[Token] = []
        self.diagnostics: list[dict] = []

    def tokenize(self) -> tuple[list[Token], list[dict]]:
        while not self._at_end():
            self._skip_trivia()
            if self._at_end():
                break
            start_line, start_col = self.line, self.col
            c = self._peek()

            if self._is_ascii_identifier_start(c):
                self._ident_or_keyword(start_line, start_col)
                continue
            if c.isdigit():
                self._number(start_line, start_col)
                continue
            if c in "\"'":
                self._string(start_line, start_col)
                continue

            # multi-char ops / ket literals
            if c == "|":
                if self._peek_at(1) == "|":
                    self._advance()
                    self._advance()
                    self.tokens.append(Token(TokenKind.OR, "||", start_line, start_col))
                    continue
                if self._peek_at(1) == ">":
                    self._advance()
                    self._advance()
                    self.tokens.append(
                        Token(TokenKind.PIPE_OP, "|>", start_line, start_col)
                    )
                    continue
                self._ket_literal(start_line, start_col)
                continue
            if c == "-" and self._peek_at(1) == ">":
                self._advance()
                self._advance()
                self.tokens.append(Token(TokenKind.ARROW, "->", start_line, start_col))
                continue
            if c == "=" and self._peek_at(1) == "=":
                self._advance()
                self._advance()
                self.tokens.append(Token(TokenKind.EQEQ, "==", start_line, start_col))
                continue
            if c == "=" and self._peek_at(1) == ">":
                self._advance()
                self._advance()
                self.tokens.append(
                    Token(TokenKind.FAT_ARROW, "=>", start_line, start_col)
                )
                continue
            if (
                c == "<"
                and self._can_start_primary()
                and self._peek_at(1) not in {"\0", " ", "\t", "\r", "\n"}
            ):
                self._bra_literal(start_line, start_col)
                continue
            if c == "&" and self._peek_at(1) == "&":
                self._advance()
                self._advance()
                self.tokens.append(Token(TokenKind.AND, "&&", start_line, start_col))
                continue
            if c == "!" and self._peek_at(1) == "=":
                self._advance()
                self._advance()
                self.tokens.append(Token(TokenKind.NEQ, "!=", start_line, start_col))
                continue
            if c == "!":
                self._advance()
                self.tokens.append(Token(TokenKind.BANG, "!", start_line, start_col))
                continue
            if c == "<" and self._peek_at(1) == "=":
                self._advance()
                self._advance()
                self.tokens.append(Token(TokenKind.LE, "<=", start_line, start_col))
                continue
            if c == ">" and self._peek_at(1) == "=":
                self._advance()
                self._advance()
                self.tokens.append(Token(TokenKind.GE, ">=", start_line, start_col))
                continue

            if c == "*" and self._peek_at(1) == "|" and self._peek_at(2) == "*":
                self._advance()
                self._advance()
                self._advance()
                self.tokens.append(
                    Token(TokenKind.TENSOR_OP, "*|*", start_line, start_col)
                )
                continue
            if c == "^":
                self._advance()
                self.tokens.append(Token(TokenKind.CARET, "^", start_line, start_col))
                continue
            if c == "." and self._peek_at(1) == ".":
                self._advance()
                self._advance()
                self.tokens.append(Token(TokenKind.RANGE, "..", start_line, start_col))
                continue

            single = {
                "+": TokenKind.PLUS,
                "-": TokenKind.MINUS,
                "*": TokenKind.STAR,
                "/": TokenKind.SLASH,
                "=": TokenKind.EQ,
                "<": TokenKind.LT,
                ">": TokenKind.GT,
                "(": TokenKind.LPAREN,
                ")": TokenKind.RPAREN,
                "{": TokenKind.LBRACE,
                "}": TokenKind.RBRACE,
                "[": TokenKind.LBRACKET,
                "]": TokenKind.RBRACKET,
                ",": TokenKind.COMMA,
                ".": TokenKind.DOT,
                ":": TokenKind.COLON,
                ";": TokenKind.SEMI,
            }
            if c in single:
                self._advance()
                self.tokens.append(Token(single[c], c, start_line, start_col))
                continue

            # unknown char — skip with error
            self._advance()
            self.diagnostics.append(
                {
                    "code": "LEX_ERROR",
                    "line": start_line,
                    "col": start_col,
                    "message": f"unexpected character {c!r}",
                }
            )
            self.tokens.append(Token(TokenKind.ERROR, c, start_line, start_col))

        self.tokens.append(Token(TokenKind.EOF, "", self.line, self.col))
        return self.tokens, self.diagnostics

    def _ket_literal(self, line: int, col: int) -> None:
        """Scan `|label>` → TokenKind.KET with literal=label."""
        self._advance()  # consume '|'
        label_start = self.i
        label = self._scan_dirac_label(stop_before=_KET_CLOSE_CHARS)
        if self._at_end() or self._peek() not in _KET_CLOSE_CHARS:
            self._emit_unterminated_dirac(
                line,
                col,
                label_start,
                message_kind="ket literal",
                expected="`>`",
            )
            return
        close = self._peek()
        self._advance()
        lexeme = f"|{label}{close}"
        self.tokens.append(Token(TokenKind.KET, lexeme, line, col, literal=label))

    def _bra_literal(self, line: int, col: int) -> None:
        """Scan adjacent ASCII `<label|` → TokenKind.BRA."""
        self._advance()  # consume '<'
        label_start = self.i
        label = self._scan_dirac_label(stop_before=frozenset("|"))
        if not label or self._at_end() or self._peek() != "|":
            self._emit_unterminated_dirac(
                line,
                col,
                label_start,
                message_kind="bra literal",
                expected="`|`",
            )
            return
        self._advance()  # '|'
        lexeme = f"<{label}|"
        self.tokens.append(Token(TokenKind.BRA, lexeme, line, col, literal=label))

    def _scan_dirac_label(self, *, stop_before: frozenset[str]) -> str:
        """Consume a ket/bra interior label; stop before a terminator or invalid char."""
        start = self.i
        while not self._at_end() and self._peek() not in stop_before:
            ch = self._peek()
            if not (self._is_ascii_identifier_part(ch) or ch in _DIRAC_LABEL_EXTRAS):
                break
            self._advance()
        return self.source[start : self.i]

    def _emit_unterminated_dirac(
        self,
        line: int,
        col: int,
        label_start: int,
        *,
        message_kind: str,
        expected: str,
    ) -> None:
        lexeme = self.source[label_start - 1 : self.i]
        self.diagnostics.append(
            {
                "code": "LEX_ERROR",
                "line": line,
                "col": col,
                "message": (
                    f"unterminated {message_kind} `{lexeme}` (expected {expected})"
                ),
            }
        )
        self.tokens.append(Token(TokenKind.ERROR, lexeme, line, col))
    def _ident_or_keyword(self, line: int, col: int) -> None:
        start = self.i
        while not self._at_end() and self._is_ascii_identifier_part(self._peek()):
            self._advance()
        lexeme = self.source[start : self.i]

        if lexeme in FORBIDDEN:
            self.diagnostics.append(
                {
                    "code": "FORBIDDEN_KEYWORD",
                    "token": lexeme,
                    "line": line,
                    "col": col,
                    "message": FORBIDDEN_MESSAGES.get(
                        lexeme, f"forbidden keyword `{lexeme}` (ADR 0035)"
                    ),
                }
            )
            self.tokens.append(Token(TokenKind.FORBIDDEN, lexeme, line, col))
            return

        if lexeme in RETIRED:
            repl = RETIRED[lexeme]
            self.diagnostics.append(
                {
                    "code": "RETIRED_KEYWORD",
                    "token": lexeme,
                    "replacement": repl,
                    "line": line,
                    "col": col,
                    "message": f"retired `{lexeme}` → use `{repl}`",
                }
            )
            self.tokens.append(
                Token(TokenKind.RETIRED, lexeme, line, col, meta={"replacement": repl})
            )
            return

        if lexeme in ACTIVE:
            self.tokens.append(Token(ACTIVE[lexeme], lexeme, line, col))
            return

        if lexeme in CONTEXTUAL:
            self.tokens.append(Token(CONTEXTUAL[lexeme], lexeme, line, col))
            return

        self.tokens.append(Token(TokenKind.IDENT, lexeme, line, col))

    def _number(self, line: int, col: int) -> None:
        start = self.i
        _, has_malformed_separator = self._digit_component()

        if not self._at_end() and self._peek() == ".":
            if self._peek_at(1).isdigit():
                self._advance()
                _, fraction_malformed = self._digit_component()
                has_malformed_separator = (
                    has_malformed_separator or fraction_malformed
                )
            elif self._peek_at(1) == "_" and self._peek_at(2).isdigit():
                # Consume the complete malformed fractional component so the
                # user receives one numeric-separator diagnostic.
                self._advance()
                self._advance()
                self._digit_component()
                has_malformed_separator = True
        if not self._at_end() and self._peek() in {"e", "E"}:
            self._advance()
            if not self._at_end() and self._peek() in {"+", "-"}:
                self._advance()
            exponent_digits, exponent_malformed = self._digit_component()
            has_malformed_separator = has_malformed_separator or exponent_malformed
            if not exponent_digits:
                if self._peek_at(0) == "_":
                    has_malformed_separator = True
                else:
                    self.diagnostics.append(
                        {
                            "code": "LEX_ERROR",
                            "line": line,
                            "col": col,
                            "message": "scientific literal requires exponent digits",
                        }
                    )
        lexeme = self.source[start : self.i]
        if has_malformed_separator:
            self._numeric_separator_error(line, col)
            self.tokens.append(Token(TokenKind.ERROR, lexeme, line, col))
            return

        normalized = lexeme.replace("_", "")
        if "." in lexeme or "e" in lexeme.lower():
            self.tokens.append(
                Token(TokenKind.FLOAT, lexeme, line, col, literal=float(normalized))
            )
            return
        self.tokens.append(
            Token(TokenKind.INT, lexeme, line, col, literal=int(normalized))
        )

    def _numeric_separator_error(self, line: int, col: int) -> None:
        self.diagnostics.append(
            {
                "code": "NUMERIC_LITERAL_SEPARATOR_ERROR",
                "line": line,
                "col": col,
                "message": "numeric separators must occur between digits",
            }
        )

    def _digit_component(self) -> tuple[bool, bool]:
        """Consume digits and separators, returning (has_digit, malformed)."""
        has_digit = False
        malformed = False
        while not self._at_end():
            if self._peek().isdigit():
                has_digit = True
                self._advance()
                continue
            if self._peek() != "_":
                break
            if not has_digit or not self._peek_at(1).isdigit():
                malformed = True
            self._advance()
        return has_digit, malformed

    def _string(self, line: int, col: int) -> None:
        quote = self._advance()
        chars: list[str] = []
        while not self._at_end() and self._peek() != quote:
            if self._peek() == "\\" and not self._at_end_at(1):
                self._advance()
                chars.append(self._advance())
            else:
                chars.append(self._advance())
        if self._at_end():
            self.diagnostics.append(
                {"code": "LEX_ERROR", "line": line, "col": col, "message": "unterminated string"}
            )
            self.tokens.append(Token(TokenKind.ERROR, "".join(chars), line, col))
            return
        self._advance()  # closing quote
        value = "".join(chars)
        self.tokens.append(Token(TokenKind.STRING, value, line, col, literal=value))

    def _skip_trivia(self) -> None:
        while not self._at_end():
            c = self._peek()
            if c in " \t\r":
                self._advance()
                continue
            if c == "\n":
                self._advance()
                continue
            if c == "/" and self._peek_at(1) == "/":
                while not self._at_end() and self._peek() != "\n":
                    self._advance()
                continue
            break

    def _at_end(self) -> bool:
        return self.i >= len(self.source)

    def _at_end_at(self, offset: int) -> bool:
        return self.i + offset >= len(self.source)

    def _peek(self) -> str:
        return self.source[self.i]

    def _peek_at(self, offset: int) -> str:
        j = self.i + offset
        if j >= len(self.source):
            return "\0"
        return self.source[j]

    def _can_start_primary(self) -> bool:
        """Return whether the current token position can begin an expression."""
        if not self.tokens:
            return True
        previous = self.tokens[-1].kind
        value_kinds = {
            TokenKind.IDENT,
            TokenKind.INT,
            TokenKind.FLOAT,
            TokenKind.STRING,
            TokenKind.KET,
            TokenKind.BRA,
            TokenKind.RPAREN,
            TokenKind.RBRACKET,
        }
        return previous not in value_kinds

    @staticmethod
    def _is_ascii_identifier_start(char: str) -> bool:
        return char == "_" or "A" <= char <= "Z" or "a" <= char <= "z"

    @staticmethod
    def _is_ascii_identifier_part(char: str) -> bool:
        return (
            Lexer._is_ascii_identifier_start(char)
            or "0" <= char <= "9"
        )

    def _advance(self) -> str:
        c = self.source[self.i]
        self.i += 1
        if c == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return c
