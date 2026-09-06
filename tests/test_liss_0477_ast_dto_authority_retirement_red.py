"""LISS-0477 / WP-0107 Phase 1 Red contracts.

These tests inventory the remaining AST/DTO authority boundaries and expose
the QASM missing-canonical-projection fallback for a later Green slice.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.codegen_qasm import OpenQASM3Generator
from compiler.staqex.lexer import Lexer
from compiler.staqex.parser import Parser
from compiler.staqex.pipeline import compile_path


SPEC = REPO / "docs/specs/staqex-scientific-semantic-core.md"
ISSUE = REPO / "docs/issues/LISS-0477-ast-dto-authority-retirement.md"
ORDINARY_GATE = REPO / "tests/fixtures/semantic_consumer_migration/ordinary_gate.sqx"


def test_ast_dto_retirement_inventory_names_each_authority_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8") + ISSUE.read_text(encoding="utf-8")
    for required in (
        "evaluator AST dispatch",
        "physics_equation",
        "EquationNode",
        "H1",
        "Algorithm Plan",
        "QASM AST/source-shape lowering",
        "migrate",
        "projection-only",
        "retire",
        "defer",
        "SSC-PROOF-AST-01",
        "SSC-PROOF-EVAL-01",
        "SSC-PROOF-QASM-01",
    ):
        assert required in text


def test_caller_created_canonical_projection_is_rejected() -> None:
    first = compile_path(ORDINARY_GATE)
    second = compile_path(ORDINARY_GATE)

    assert first.scientific_semantic_ir is not None
    assert second.scientific_semantic_ir is not None
    emitted = OpenQASM3Generator(route=False).generate_detailed(
        first.unit,
        semantic_ir=second.scientific_semantic_ir,
    )

    assert not emitted.ok
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"
    assert emitted.qasm == ""
    assert emitted.circuit.allocation_started is False


def test_missing_canonical_projection_fails_closed_before_qasm_artifact() -> None:
    source = ORDINARY_GATE.read_text(encoding="utf-8")
    tokens, lex_diagnostics = Lexer(source).tokenize()
    unit = Parser(tokens).parse()

    assert lex_diagnostics == []
    emitted = OpenQASM3Generator(route=False).generate_detailed(unit)

    assert not emitted.ok
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"
    assert emitted.qasm == ""
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False


def test_canonical_projection_retains_identity_role_dimensions_and_provenance() -> None:
    compiled = compile_path(ORDINARY_GATE)

    assert compiled.scientific_semantic_ir is not None
    canonical = compiled.scientific_semantic_ir
    assert canonical.source_unit_identity == id(compiled.unit)
    assert canonical.nodes
    assert all(node.node_id for node in canonical.nodes)
    assert all(node.role_lane for node in canonical.nodes)
    assert all(node.type for node in canonical.nodes)
    assert all(node.provenance.source for node in canonical.nodes)
