"""AT-TDD Phase 1 Red: LISS-0487 Equation DTO authority retirement."""

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.hir import build_hir
from compiler.staqex.physics_equation import Coefficient, EquationNode, Unit
from compiler.staqex.physics_ir import SourceOrigin
from compiler.staqex.physics_ir_lower import lower_hir_to_physics_ir
from compiler.staqex.pipeline import compile_source


SPEC = REPO / "docs/specs/staqex-scientific-semantic-consumer-migration.md"


def test_equation_dto_spec_defines_diagnostic_only_authority() -> None:
    text = SPEC.read_text(encoding="utf-8")

    assert "### LISS-0487 Equation DTO authority retirement" in text
    for requirement in (
        "caller-injected",
        "no finite artifact or execution authorization",
        "Scientific Semantic IR",
        "string equation payloads",
    ):
        assert requirement in text


def test_injected_equation_is_marked_diagnostic_only_in_physics_projection() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X + Z
            State psi = |0>
            Measure psi
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    assert compiled.checker is not None
    assert compiled.unit is not None
    hir = build_hir(compiled.checker, unit=compiled.unit)
    origin = SourceOrigin(source_id="caller.sqx", line=1, col=1)
    unit = Unit(symbol="J", dimensions=(1, 1, -2), origin=origin)
    injected = EquationNode(
        kind="equality",
        left="H",
        right="omega * N",
        coefficients=(Coefficient(expression="omega", unit=unit, origin=origin),),
        origin=origin,
    )

    lowered = lower_hir_to_physics_ir(hir, unit=compiled.unit, equations=(injected,))

    assert lowered.metadata["semantic_authority"] == "scientific_semantic_ir"
    assert lowered.metadata["equation_dto_role"] == "diagnostic_only"
    assert lowered.metadata["injected_equation_authorized"] is False


def test_string_equation_has_no_implicit_semantic_conversion() -> None:
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

    try:
        lower_hir_to_physics_ir(
            build_hir(compiled.checker, unit=compiled.unit),
            unit=compiled.unit,
            equations=("H = omega * N",),
        )
    except TypeError as exc:
        assert "EquationNode" in str(exc)
    else:
        raise AssertionError("string equations must not be implicitly converted")
