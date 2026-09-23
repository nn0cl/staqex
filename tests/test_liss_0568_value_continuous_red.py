"""Phase 1 Red contracts for the value/continuous body successor."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Any, Mapping

from compiler.staqex.continuous_field import ContinuousFieldValue
from compiler.staqex.host import run_source
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluator import Evaluator
from compiler.staqex.runtime.joint import Joint


PACKAGE = "compiler.staqex.runtime.evaluation"
REPO = Path(__file__).resolve().parents[1]


def _binds(compiled: Any) -> dict[str, Any]:
    return {
        stmt.names[0]: stmt.expr
        for stmt in compiled.unit.main.body.stmts
        if hasattr(stmt, "names")
    }


class _FakeContinuousFieldAdapter:
    def field(self, source: str, domain: str) -> str:
        return f"host-ref::{source}::{domain}"

    def discretize(
        self,
        value: ContinuousFieldValue,
        *,
        lo: float,
        hi: float,
        n_bins: int,
        seed: int | None,
    ) -> Mapping[Any, float]:
        return {index: 1.0 / n_bins for index in range(n_bins)}


def test_value_continuous_successors_expose_bounded_entrypoints() -> None:
    classical = importlib.import_module(f"{PACKAGE}.classical")
    continuous = importlib.import_module(f"{PACKAGE}.continuous")
    for name in (
        "evaluate_value",
        "evaluate_value_with_unit",
        "resolve_attribute",
    ):
        assert callable(getattr(classical, name, None)), name
    for name in (
        "bind_finiteize",
        "bind_finiteize_continuous",
        "bind_field_from_host",
        "bind_continuous_compose",
    ):
        assert callable(getattr(continuous, name, None)), name


def test_value_continuous_successors_have_no_public_facade_dependency() -> None:
    for module_name in ("classical", "continuous"):
        module = importlib.import_module(f"{PACKAGE}.{module_name}")
        source = inspect.getsource(module)
        assert "runtime.evaluator" not in source
        assert "from ..evaluator" not in source
        assert "Evaluator(" not in source


def test_context_declares_value_and_continuous_callbacks() -> None:
    context = inspect.getsource(importlib.import_module(f"{PACKAGE}.context"))
    for callback in (
        "_evaluate_nested_value",
        "_value_environment",
        "_continuous_field_port",
        "_runtime_seed",
        "_store_runtime_object",
    ):
        assert f"def {callback}" in context


def test_compatibility_wires_value_and_continuous_successors() -> None:
    compatibility = inspect.getsource(
        importlib.import_module(f"{PACKAGE}.compatibility")
    )
    assert "install_value_compatibility" in compatibility
    assert "install_continuous_compatibility" in compatibility


def test_successors_do_not_define_a_second_mutable_state_owner() -> None:
    for module_name in ("classical", "continuous"):
        module = importlib.import_module(f"{PACKAGE}.{module_name}")
        source = inspect.getsource(module)
        assert "self.objects" not in source
        assert "self.scalars" not in source
        assert "self._this" not in source


def test_classical_value_characterization_remains_successful() -> None:
    compiled = compile_source(
        """
package t
pub fn main() -> Unit {
  State<Int> value = Dirac(1)
  Measure value
}
"""
    )
    assert compiled.ok, compiled.diagnostics
    result = run_source(
        """
package t
pub fn main() -> Unit {
  State<Int> value = Dirac(1)
  Measure value
}
""",
        settings={"seed": 0},
    )
    assert result.status == "succeeded", result.diagnostics


def test_continuous_finiteize_characterization_remains_successful() -> None:
    compiled = compile_source(
        """
package t
pub fn main() -> Unit {
  Continuous damage = field_from_host("damage_proxy_v1", "Omega")
  State zone = finiteize(damage, 0.0, 1.0, 3, 0)
  Measure zone
}
"""
    )
    assert compiled.ok, compiled.diagnostics
    binds = _binds(compiled)
    evaluator = Evaluator(
        seed=0, continuous_field=_FakeContinuousFieldAdapter()
    )
    joint = Joint.unit()
    joint = evaluator._bind_names(
        joint, ["damage"], binds["damage"], logs=[], inspect_out=None
    )
    joint = evaluator._bind_names(
        joint, ["zone"], binds["zone"], logs=[], inspect_out=None
    )
    assert {world.assign["zone"] for world in joint.worlds} == {0, 1, 2}


def test_continuous_provenance_characterization_remains_successful() -> None:
    compiled = compile_source(
        """
package t
pub fn main() -> Unit {
  Continuous damage = field_from_host("damage_proxy_v1", "Omega")
  Continuous flood = field_from_host("inundation_v1", "Omega")
  Continuous risk = weight(damage, flood)
  State zone = finiteize(risk, 0.0, 1.0, 2, 0)
  Measure zone
}
"""
    )
    assert compiled.ok, compiled.diagnostics
    binds = _binds(compiled)
    evaluator = Evaluator(
        seed=0, continuous_field=_FakeContinuousFieldAdapter()
    )
    joint = Joint.unit()
    for name in ("damage", "flood", "risk", "zone"):
        joint = evaluator._bind_names(
            joint, [name], binds[name], logs=[], inspect_out=None
        )
    provenance = evaluator.objects["__finiteize_prov_zone"]
    assert provenance["continuous_pipeline"] == ("weight",)
    assert provenance["discretization"]["resolution"] == 2
