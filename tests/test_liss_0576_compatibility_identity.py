"""Passing hook identity checks for LISS-0576's accepted Red boundary."""

from compiler.staqex.runtime.evaluation import assignments, continuous
from compiler.staqex.runtime.evaluator import Evaluator


def test_continuous_hooks_are_installed_from_the_successor_module() -> None:
    assert Evaluator._bind_finiteize is continuous.bind_finiteize
    assert Evaluator._bind_finiteize_continuous is continuous.bind_finiteize_continuous
    assert Evaluator._bind_field_from_host is continuous.bind_field_from_host
    assert Evaluator._bind_continuous_compose is continuous.bind_continuous_compose


def test_assignment_hook_is_installed_from_the_successor_module() -> None:
    assert Evaluator._execute_assignment is assignments.execute_assignment
