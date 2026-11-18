"""Phase 1 Red contracts for splitting the static Unitarity pass.

Behavior checks characterize the currently accepted pass through its actual
public and pipeline consumers. The structural check deliberately fails until
the private implementation helpers have a single owner outside the public
compatibility module. No production module layout is prescribed.
"""

from __future__ import annotations

import ast
import importlib
from pathlib import Path
import sys

import pytest

from compiler.staqex import pipeline_legacy
from compiler.staqex.ast_nodes import CompilationUnit, Span
from compiler.staqex.pipeline import compile_source
from compiler.staqex.unitarity_check import check_unitarity


_REPO = Path(__file__).resolve().parents[1]
_SOURCE_MODULE = _REPO / "compiler/staqex/unitarity_check.py"
_IMPLEMENTATION_HELPERS = {
    "_check_measure_target",
    "_expr_is_classical_scalar",
    "_check_expr_unitarity",
    "_expr_is_transparent",
    "_fn_body_is_transparent",
    "_check_apply_unitary",
    "_check_hamiltonian_hermitian",
    "_is_unitary",
    "_is_hermitian",
    "_expr_is_quantum",
    "_lambda_is_constant",
    "_lambda_collapses_bits",
    "_eval_lambda_bit",
    "_eval_closed_arith",
    "_mentions_name",
    "_is_closed_value",
    "_when_collapses",
    "_is_numeric_lit",
    "_lit_value",
    "_op_name",
    "_children",
}


def _unitarity_diagnostics(source: str) -> list[dict[str, object]]:
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    return check_unitarity(compiled.unit)


def _codes(diagnostics: list[dict[str, object]]) -> list[str]:
    return [str(diagnostic["code"]) for diagnostic in diagnostics]


def test_pipeline_keeps_the_public_unitarity_entrypoint() -> None:
    """The production pipeline and public facade retain the same callable."""
    assert pipeline_legacy.check_unitarity is check_unitarity
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator Bad = 2.0 * X
            State psi = |0>
            State bad = apply(Bad, psi)
            Measure bad
        }
        """
    )
    assert compiled.unit is not None, compiled.diagnostics
    assert "NON_UNITARY_TRANSFORM_ERROR" in _codes(compiled.diagnostics)


def test_unitarity_pass_is_empty_when_the_unit_has_no_main() -> None:
    unit = CompilationUnit(
        package=None,
        imports=[],
        decls=[],
        main=None,
        span=Span(line=1, col=1),
    )
    assert check_unitarity(unit) == []


def test_nested_diagnostics_keep_depth_first_emission_order_and_spans() -> None:
    diagnostics = _unitarity_diagnostics(
        """
        package t
        pub fn main() -> Unit {
            Operator Bad = 2.0 * X
            State psi = |+>
            State out = apply(Bad, project(psi, x -> x == 0))
            Measure out
        }
        """
    )
    assert diagnostics == [
        {
            "code": "NON_UNITARY_TRANSFORM_ERROR",
            "line": 6,
            "col": 31,
            "message": "`apply`/`capply` matrix for `Bad` is not unitary "
            "(U†U ≉ I). Use a unitary Operator or gate (Hadamard, Pauli, S, T).",
        },
        {
            "code": "PREDICATE_PROJECTOR_ERROR",
            "line": 6,
            "col": 44,
            "message": "`project` is the Hilbert projector |k⟩⟨k|, not a "
            "classical predicate filter. Write project(psi, 0) or "
            "project(psi, |0>).",
        },
    ]


def test_quantum_map_rejects_bit_collapse_but_accepts_bit_flip() -> None:
    bad = _unitarity_diagnostics(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            State bad = map(psi, x -> 0)
            Measure bad
        }
        """
    )
    good = _unitarity_diagnostics(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            State ok = map(psi, x -> 1 - x)
            Measure ok
        }
        """
    )
    assert _codes(bad) == ["NON_UNITARY_TRANSFORM_ERROR"]
    assert good == []


def test_project_keeps_predicate_rejection_and_hilbert_projection_acceptance() -> None:
    rejected = _unitarity_diagnostics(
        """
        package t
        pub fn main() -> Unit {
            State psi = |+>
            State bad = project(psi, x -> x == 0)
            Measure bad
        }
        """
    )
    accepted = _unitarity_diagnostics(
        """
        package t
        pub fn main() -> Unit {
            State psi = |0>
            State projected = project(psi, |0>)
            Measure projected
        }
        """
    )
    assert _codes(rejected) == ["PREDICATE_PROJECTOR_ERROR"]
    assert accepted == []


def test_classical_scalar_measurement_remains_rejected() -> None:
    diagnostics = _unitarity_diagnostics(
        """
        package t
        pub fn main() -> Unit {
            Float observed = 1.0
            Measure observed
        }
        """
    )
    assert _codes(diagnostics) == ["CANNOT_MEASURE_CLASSICAL_VALUE_ERROR"]
    assert diagnostics[0]["line"] == 5
    assert diagnostics[0]["col"] == 21


def test_known_unitary_operator_is_not_rejected() -> None:
    diagnostics = _unitarity_diagnostics(
        """
        package t
        pub fn main() -> Unit {
            Operator Had = 0.7071067811865476 * (X + Z)
            State psi = |0>
            State result = apply(Had, psi)
            Measure result
        }
        """
    )
    assert diagnostics == []


def test_phase1_structure_moves_recursive_walker_out_of_public_module() -> None:
    """A thin public owner must not retain helper implementation bodies.

    Destination filenames are intentionally unrestricted: this contract is
    about unique ownership and a readable compatibility module, not a guessed
    module layout.
    """
    tree = ast.parse(_SOURCE_MODULE.read_text(encoding="utf-8"))
    module_functions = {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    retained_helpers = sorted(module_functions & _IMPLEMENTATION_HELPERS)
    assert retained_helpers == [], (
        "private Unitarity implementation bodies still live in the public "
        f"facade: {retained_helpers}"
    )

    package_sources = sorted((_REPO / "compiler/staqex").rglob("*.py"))
    definitions: dict[str, list[Path]] = {name: [] for name in _IMPLEMENTATION_HELPERS}
    for source_path in package_sources:
        source_tree = ast.parse(source_path.read_text(encoding="utf-8"))
        for node in source_tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name in definitions:
                    definitions[node.name].append(source_path)

    duplicate_owners = {
        name: [path.relative_to(_REPO).as_posix() for path in paths]
        for name, paths in definitions.items()
        if len(paths) > (2 if name == "_children" else 1)
    }
    assert duplicate_owners == {}, f"multiple live helper owners: {duplicate_owners}"


FOLLOW_ON_TEST_PATH = "tests/test_liss_0594_unitarity_family_red.py"


def test_guard_compatibility_declares_one_exact_follow_on_path() -> None:
    """The 0594 test is downstream inventory, not part of 0593 semantics."""
    guard = importlib.import_module("tests.liss_0593_guard_support")
    assert guard.FOLLOW_ON_TESTS == {FOLLOW_ON_TEST_PATH}
    assert FOLLOW_ON_TEST_PATH not in guard.NEW_TESTS
    assert guard.new_test_paths() == (
        guard.NEW_TESTS | guard.NEW_FIXTURES | {FOLLOW_ON_TEST_PATH}
    )


def test_historical_reader_accepts_follow_on_without_expanding_old_cohort() -> None:
    primary = importlib.import_module("tests.liss_0591_guard_support")
    actual = primary.subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "tests"],
        cwd=primary.ROOT,
        text=True,
    ).splitlines()
    assert set(primary.historical_test_paths(actual)) == set(
        primary.baseline()["test_paths"]
    )


@pytest.mark.parametrize("mode", ["unlisted", "artifact-missing"])
def test_follow_on_inventory_has_positive_and_missing_artifact_controls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    composition = importlib.import_module(
        "tests.test_liss_0593_guard_composition_red"
    )
    helper, primary = composition.g_stage(tmp_path / "stage", monkeypatch)
    path = composition.FOLLOW_ON_TEST_PATH
    assert (helper.ROOT / path).is_file()
    assert path in helper.new_test_paths()

    _, actual = composition.g_follow_on_listing(primary, monkeypatch)
    if mode == "unlisted":
        actual.remove(path)
    else:
        (helper.ROOT / path).unlink()
    monkeypatch.setattr(
        primary.subprocess,
        "check_output",
        lambda *args, **kwargs: "\n".join(sorted(actual)) + "\n",
    )
    with pytest.raises(AssertionError):
        primary.historical_test_paths(sorted(actual))


@pytest.mark.parametrize(
    "first", ["liss_0591_guard_support", "liss_0593_guard_support"]
)
def test_follow_on_stays_outside_the_26_path_semantic_cohort(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, first: str
) -> None:
    composition = importlib.import_module(
        "tests.test_liss_0593_guard_composition_red"
    )
    helper, primary = composition.g_stage(tmp_path / "stage", monkeypatch)
    tests, fixtures = composition.g_original_additions()
    assert primary.NEW_TESTS == tests | helper.NEW_TESTS
    assert primary.NEW_FIXTURES == fixtures | helper.NEW_FIXTURES
    assert len(primary.NEW_TESTS | primary.NEW_FIXTURES) == 26
    assert helper.NEW_TESTS == composition.SEMANTIC_TESTS
    assert helper.NEW_FIXTURES == composition.SEMANTIC_FIXTURES
    assert helper.FOLLOW_ON_TESTS == {composition.FOLLOW_ON_TEST_PATH}
    assert composition.FOLLOW_ON_TEST_PATH not in (
        helper.NEW_TESTS | helper.NEW_FIXTURES
    )
    assert helper.new_test_paths() == (
        helper.NEW_TESTS
        | helper.NEW_FIXTURES
        | {composition.FOLLOW_ON_TEST_PATH}
    )
    helper.assert_inverse_closure(helper.ROOT)
    command = [
        sys.executable,
        "-c",
        "import sys,tests,importlib; tests.__path__=["
        + repr(str(helper.ROOT / "tests"))
        + "]; importlib.import_module('tests."
        + first
        + "'); p=importlib.import_module('tests.liss_0591_guard_support'); "
        "s=importlib.import_module('tests.liss_0593_guard_support'); "
        "assert s.NEW_TESTS <= p.NEW_TESTS and s.NEW_FIXTURES <= p.NEW_FIXTURES",
    ]
    result = composition.subprocess.run(
        command, cwd=composition.guard.ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_guard_compatibility_rejects_a_missing_follow_on_artifact(
    tmp_path: Path, monkeypatch
) -> None:
    guard = importlib.import_module("tests.liss_0593_guard_support")
    monkeypatch.setattr(guard, "ROOT", tmp_path)
    expected_paths = guard.NEW_TESTS | guard.NEW_FIXTURES | guard.FOLLOW_ON_TESTS
    for relative in expected_paths - {FOLLOW_ON_TEST_PATH}:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"fixture")

    with pytest.raises(AssertionError, match="artifact missing"):
        guard.new_test_paths()
