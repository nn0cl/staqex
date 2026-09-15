"""Phase 1 Red contracts for Parser family extraction."""

from __future__ import annotations

import importlib
import inspect
import re
from pathlib import Path

from compiler.staqex.parser import Parser


REPOSITORY = Path(__file__).resolve().parents[1]
PARSER_SOURCE = REPOSITORY / "compiler/staqex/parser.py"
FAMILY_ENTRYPOINTS = {
    "cursor": "peek",
    "top_level": "parse_declaration",
    "scientific": "parse_scientific_scope",
    "statements": "parse_statement",
    "expressions": "parse_expression",
    "operators": "parse_operator_expression",
    "recovery": "recover_top_level",
}


def _module_source(name: str) -> str:
    path = REPOSITORY / "compiler/staqex/parsing" / f"{name}.py"
    return path.read_text(encoding="utf-8")


def test_parser_family_modules_expose_named_entrypoints() -> None:
    missing: list[str] = []
    for module_name, entrypoint in FAMILY_ENTRYPOINTS.items():
        try:
            module = importlib.import_module(
                f"compiler.staqex.parsing.{module_name}"
            )
        except ModuleNotFoundError:
            missing.append(f"{module_name}.{entrypoint}")
            continue
        if not callable(getattr(module, entrypoint, None)):
            missing.append(f"{module_name}.{entrypoint}")

    assert not missing, f"missing parser entrypoints: {missing}"


def test_parser_facade_does_not_retain_family_bodies() -> None:
    source = inspect.getsource(Parser)

    for method_name in (
        "_primary",
        "_stmt",
        "_op_primary",
        "_h1_scope_decl",
        "_skip_until_toplevel_resync",
    ):
        assert re.search(
            rf"^\s+def {re.escape(method_name)}\(",
            source,
            re.MULTILINE,
        ) is None


def test_parser_family_modules_depend_on_shared_context_not_facade() -> None:
    context = importlib.import_module("compiler.staqex.parsing.context")
    assert hasattr(context, "ParserContext")

    for module_name in FAMILY_ENTRYPOINTS:
        source = _module_source(module_name)
        assert "staqex.parser" not in source
        assert "from ..parser" not in source


def test_parser_context_declares_shared_cursor_and_diagnostic_contract() -> None:
    context_source = _module_source("context")

    for callback_name in (
        "_peek",
        "_advance",
        "_expect",
        "_emit_diagnostic",
        "_recover_top_level",
    ):
        assert f"def {callback_name}" in context_source

