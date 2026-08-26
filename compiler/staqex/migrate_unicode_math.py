"""Normalize historical Unicode quantum spellings to ASCII source.

This is an explicit migration tool, not a lexer fallback. New source remains
ASCII-only under ADR 0191.
"""

from __future__ import annotations

_UNICODE_KET_CLOSE = "\u27e9"  # ⟩
_UNICODE_TENSOR = "\u2297"  # ⊗
_UNICODE_DAGGER = "\u2020"  # †
_UNICODE_BRA_OPEN = "\u27e8"  # ⟨
_ASCII_TENSOR = "*|*"
_UNICODE_IDENTIFIERS = {"ψ": "psi", "φ": "phi", "ρ": "rho"}


def migrate_unicode_math_source(source: str) -> str:
    """Convert historical Unicode quantum source forms to ASCII.

    Comments and string literals are copied verbatim. The transformation is
    deterministic and idempotent on ASCII source.
    """

    out: list[str] = []
    i = 0
    while i < len(source):
        if source.startswith("//", i):
            i = _copy_line_comment(source, i, out)
            continue
        if source[i] in {"'", '"'}:
            i = _copy_string_literal(source, i, out)
            continue
        if source.startswith(_UNICODE_TENSOR, i):
            out.append(_ASCII_TENSOR)
            i += 1
            continue
        if source.startswith(_UNICODE_BRA_OPEN, i):
            end = source.find("|", i + 1)
            if end >= 0:
                out.append("<")
                out.append(source[i + 1 : end])
                out.append("|")
                i = end + 1
                continue
        if source.startswith(_UNICODE_KET_CLOSE, i):
            out.append(">")
            i += 1
            continue
        if source.startswith(_UNICODE_DAGGER, i):
            identifier, start = _previous_identifier(source, i)
            if identifier is not None:
                # The identifier has already been emitted. Replace its suffix
                # in the output with the explicit callable spelling.
                rendered = "".join(out)
                if rendered.endswith(identifier):
                    out[:] = [rendered[: -len(identifier)], f"adjoint({identifier})"]
                    i += 1
                    continue
        if source[i] in _UNICODE_IDENTIFIERS:
            out.append(_UNICODE_IDENTIFIERS[source[i]])
            i += 1
            continue
        out.append(source[i])
        i += 1
    return "".join(out)


def _copy_line_comment(source: str, i: int, out: list[str]) -> int:
    start = i
    while i < len(source) and source[i] != "\n":
        i += 1
    out.append(source[start:i])
    return i


def _copy_string_literal(source: str, i: int, out: list[str]) -> int:
    quote = source[i]
    start = i
    i += 1
    while i < len(source):
        if source[i] == "\\":
            i += 2
            continue
        if source[i] == quote:
            i += 1
            break
        i += 1
    out.append(source[start:i])
    return i


def _previous_identifier(source: str, dagger_index: int) -> tuple[str | None, int]:
    end = dagger_index
    start = end
    while start > 0 and (source[start - 1].isalnum() or source[start - 1] == "_"):
        start -= 1
    if start == end:
        return None, 0
    return source[start:end], start
