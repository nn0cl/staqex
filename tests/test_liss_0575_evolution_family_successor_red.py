"""Phase 1 Red contracts for WP-0168 / LISS-0575."""

from __future__ import annotations

import ast
import io
from pathlib import Path

from compiler.staqex.ast_nodes import Call, Span, Var
from compiler.staqex.continuous_lowering import GridHamiltonian
from compiler.staqex.host import run_source
from compiler.staqex.runtime.evaluator import Evaluator
from compiler.staqex.runtime.evaluation.evolution import joint_l2_distance
from compiler.staqex.runtime.joint import Joint, World
from compiler.staqex.stdlib.prelude import HBAR_SI


ROOT = Path(__file__).resolve().parents[1]
EVOLUTION = ROOT / "compiler/staqex/runtime/evaluation/evolution.py"
UNITARY = ROOT / "compiler/staqex/runtime/evaluation/unitary_ops.py"
ORCHESTRATION = ROOT / "compiler/staqex/runtime/evaluation/evolution_ops.py"
HAMILTONIAN = ROOT / "compiler/staqex/runtime/evaluation/hamiltonian_evolution.py"
COMPATIBILITY = ROOT / "compiler/staqex/runtime/evaluation/compatibility.py"
CONTEXT = ROOT / "compiler/staqex/runtime/evaluation/context.py"


SUCCESSOR_SYMBOLS = {
    UNITARY: {
        "bind_apply_multi", "bind_cnot_multi", "resolve_unitary_matrix",
        "qft_family_matrix", "bind_apply", "is_unitary_name",
        "split_capply_args", "bind_capply",
    },
    ORCHESTRATION: {
        "ExplicitPropagator", "explicit_propagator", "bind_evolve",
        "bind_explicit_evolve", "eval_max_steps", "eval_until_predicate",
        "bind_evolve_hamiltonian",
    },
    HAMILTONIAN: {
        "hamiltonian_evolve_one_step",
        "hamiltonian_evolve_tuple_coordinate", "evolve_precomputed_grid",
    },
}


def _top_level_symbol_names(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def _assert_successor_owns_symbols(path: Path) -> None:
    assert path.is_file(), f"missing successor: {path.name}"
    successor_symbols = _top_level_symbol_names(path)
    original_symbols = _top_level_symbol_names(EVOLUTION)
    assert SUCCESSOR_SYMBOLS[path] <= successor_symbols
    assert not (SUCCESSOR_SYMBOLS[path] & original_symbols)
    source = path.read_text(encoding="utf-8")
    assert "runtime.evaluator" not in source
    assert "from ..evaluator" not in source
    assert "Evaluator(" not in source


def test_unitary_successor_owns_unitary_bodies() -> None:
    _assert_successor_owns_symbols(UNITARY)


def test_evolution_successor_owns_orchestration_bodies() -> None:
    _assert_successor_owns_symbols(ORCHESTRATION)


def test_hamiltonian_successor_owns_hamiltonian_bodies() -> None:
    _assert_successor_owns_symbols(HAMILTONIAN)


def test_evolution_compatibility_wiring_is_declared() -> None:
    tree = ast.parse(COMPATIBILITY.read_text(encoding="utf-8"))
    imports = {
        node.module: {alias.name for alias in node.names}
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
    }
    expected = {
        "unitary_ops": SUCCESSOR_SYMBOLS[UNITARY],
        "evolution_ops": SUCCESSOR_SYMBOLS[ORCHESTRATION],
        "hamiltonian_evolution": SUCCESSOR_SYMBOLS[HAMILTONIAN],
    }
    for module, names in expected.items():
        assert names <= imports.get(module, set())


def test_evolution_context_declares_narrow_boundaries() -> None:
    source = CONTEXT.read_text(encoding="utf-8")
    for callback in (
        "_unitary_operator_definition",
        "_unitary_operator_environment",
        "_static_register_size",
        "_eval_value_with_unit",
        "_eval_times",
        "_evolve_precomputed_grid",
        "_hamiltonian_evolve_tuple_coordinate",
    ):
        assert f"def {callback}" in source


def test_unitary_apply_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State q = |0>
  State q = apply(H, q)
  Measure q
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_explicit_evolution_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  Energy scale = 1.0.eV to J
  Operator H = scale * X
  Time dur = 0.1.fs
  Operator U = exp(-i * H * dur / hbar)
  State q = |0>
  State q = Evolve() { U * q }.run()
  Measure q
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_cnot_multi_characterization_remains_successful() -> None:
    evaluator = Evaluator(seed=0)
    joint = Joint(
        worlds=[World(assign={"c": 1, "t": 0}, amp=1 + 0j)]
    )
    span = Span(line=1, col=1)
    expr = Call(
        callee=Var(name="cnot", span=span),
        args=[Var(name="c", span=span), Var(name="t", span=span)],
        span=span,
    )
    updated = evaluator._bind_cnot_multi(joint, ["c", "t"], expr)
    assert updated.worlds[0].assign == {"c": 1, "t": 1}


def test_controlled_apply_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State control = |1>
  State target = |0>
  State target = capply(control, X, target)
  Measure target
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_hamiltonian_evolution_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State q = |0>
  State q = Evolve { (q) under X for 0.1.fs }.run()
  Measure q
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_tuple_coordinate_hamiltonian_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  Energy scale = 1.0.eV to J
  Operator H = scale * (1.0 * Z[0] + 1.0 * X[0] + 1.0 * (Z[0] * Z[1]))
  State psi = prepare_selection(2)
  State psi = Evolve { psi under H for 0.6.fs }.run()
  Measure psi
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_bounded_explicit_evolution_characterization_remains_successful() -> None:
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State psi = |0>
  Energy scale = 0.0.eV to J
  Operator H = scale * X
  Time dur = 0.1.fs
  Operator U = exp(-i * H * dur / hbar)
  State result = Evolve() { U * psi until converged(psi) max 2 }.run()
  Measure result
}
""",
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_joint_distance_characterization_remains_zero_for_equal_states() -> None:
    left = Joint(worlds=[World(assign={"q": 0}, amp=1 + 0j)])
    right = Joint(worlds=[World(assign={"q": 0}, amp=1 + 0j)])
    assert joint_l2_distance(left, right) == 0.0


def test_precomputed_grid_evolution_characterization_remains_successful() -> None:
    evaluator = Evaluator(seed=0)
    amplitude = 2 ** -0.5
    joint = Joint(
        worlds=[
            World(assign={"x": 0.0}, amp=amplitude + 0j),
            World(assign={"x": 1.0}, amp=amplitude + 0j),
        ]
    )
    grid = GridHamiltonian(
        alias="H_grid",
        contract="position-grid",
        source="H",
        xs=(0.0, 1.0),
        matrix=((0j, 1 + 0j), (1 + 0j, 0j)),
    )

    evolved = evaluator._evolve_precomputed_grid(
        joint, ["x"], grid, HBAR_SI * (3.141592653589793 / 2)
    )
    amplitudes = evolved.amplitude_marginal("x")
    assert abs(amplitudes[0.0] + 1j * amplitude) < 1e-12
    assert abs(amplitudes[1.0] + 1j * amplitude) < 1e-12


def test_qft_characterization_remains_available_through_evaluator() -> None:
    evaluator = Evaluator(seed=0)
    evaluator.static_register_sizes["r"] = 1
    span = Span(line=1, col=1)
    expr = Call(
        callee=Var(name="qft", span=span),
        args=[Var(name="r", span=span)],
        span=span,
    )
    matrix = evaluator._qft_family_matrix(expr, 1)
    assert len(matrix) == 2
    assert len(matrix[0]) == 2
