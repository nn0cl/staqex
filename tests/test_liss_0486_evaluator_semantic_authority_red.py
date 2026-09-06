"""AT-TDD Phase 1 Red: LISS-0486 evaluator semantic authority."""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator


SPEC = REPO / "docs/specs/staqex-scientific-semantic-consumer-migration.md"


def test_evaluator_migration_spec_defines_canonical_runtime_boundary() -> None:
    text = SPEC.read_text(encoding="utf-8")

    assert "### LISS-0486 evaluator semantic-authority migration" in text
    for requirement in (
        "compile-owned `ScientificSemanticIR`",
        "terminal `measure`",
        "no fabricated runtime result",
        "automatic finiteization",
    ):
        assert requirement in text


def test_evaluator_receives_compile_owned_semantic_ir_identity() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            Measure psi
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    canonical = compiled.scientific_semantic_ir
    assert canonical is not None
    evaluator = Evaluator(seed=0)

    result = evaluator.run_canonical_unit(compiled.unit, semantic_ir=canonical)

    assert result.measure is not None
    assert evaluator.semantic_ir is canonical


def test_evaluator_rejects_caller_injected_semantic_ir() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            Measure psi
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    canonical = compiled.scientific_semantic_ir
    assert canonical is not None
    forged = object()
    evaluator = Evaluator(seed=0)

    try:
        evaluator.run_canonical_unit(compiled.unit, semantic_ir=forged)
    except ValueError as exc:
        assert "ScientificSemanticIR" in str(exc)
    else:
        raise AssertionError("caller-injected semantic IR must be rejected")
