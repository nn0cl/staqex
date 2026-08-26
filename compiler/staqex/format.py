"""Canonical source formatting for the ASCII source surface."""

from __future__ import annotations


def format_source(source: str) -> str:
    """Preserve ASCII source spelling while formatting remains lossless.

    Unicode-to-ASCII migration is a separate explicit tool operation. The
    formatter must never emit source that the lexer rejects.
    """

    return source
