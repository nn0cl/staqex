"""AT-TDD: LISS-0235 Kernel RngPort (ADR 0170)."""

from __future__ import annotations

import ast
import io
import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.rng_port import RngPort, StdlibRngAdapter  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime import evaluator as evaluator_mod  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_stdlib_adapter_implements_rng_port() -> None:
    port: RngPort = StdlibRngAdapter(seed=0)
    assert 0.0 <= port.random() < 1.0


def test_evaluator_does_not_construct_random_random() -> None:
    """After Green, evaluator.py must not call random.Random(...)."""
    source = Path(evaluator_mod.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute) and func.attr == "Random":
                if isinstance(func.value, ast.Name) and func.value.id == "random":
                    hits.append(f"line {node.lineno}")
    assert hits == [], f"evaluator still constructs random.Random: {hits}"


def test_seeded_measure_bit_identical_across_runs() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State a = Coin()
        Measure a
    }
    """
    first = run_source(src, seed=0, stdout=io.StringIO())
    second = run_source(src, seed=0, stdout=io.StringIO())
    assert first.compile_ok and second.compile_ok
    assert first.eval.measure is not None and second.eval.measure is not None
    assert first.eval.measure.value == second.eval.measure.value
    assert first.eval.measure.output == second.eval.measure.output


def test_seed_zero_example_cli_output_stable() -> None:
    """Published example --seed 0 output must match a pinned fixture string."""
    example = (
        _REPO
        / "examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx"
    )
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "compiler.staqex",
            "run",
            str(example),
            "--seed",
            "0",
        ],
        cwd=_REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    # Pin the full stdout so refactors cannot silently reshape seeded output.
    assert proc.stdout == "42\n"


def test_custom_rng_port_is_used_for_measure() -> None:
    class FixedRng:
        def __init__(self, values: list[float]) -> None:
            self._values = list(values)

        def random(self) -> float:
            return self._values.pop(0)

    src = """
    package t
    pub fn main() -> Unit {
        State a = Coin()
        Measure a
    }
    """
    from compiler.staqex.pipeline import compile_source

    compiled = compile_source(src)
    assert compiled.ok and compiled.unit is not None
    ev = Evaluator(rng_port=FixedRng([0.9]))
    result = ev.run_unit(compiled.unit, stdout=io.StringIO())
    assert result.measure is not None
    # Coin() is 50/50 on {0,1}; u=0.9 selects the second mass atom (1).
    assert result.measure.value == 1


if __name__ == "__main__":
    test_stdlib_adapter_implements_rng_port()
    print("PASS test_stdlib_adapter_implements_rng_port")
    test_seeded_measure_bit_identical_across_runs()
    print("PASS test_seeded_measure_bit_identical_across_runs")
    test_seed_zero_example_cli_output_stable()
    print("PASS test_seed_zero_example_cli_output_stable")
    test_custom_rng_port_is_used_for_measure()
    print("PASS test_custom_rng_port_is_used_for_measure")
    test_evaluator_does_not_construct_random_random()
    print("PASS test_evaluator_does_not_construct_random_random")
    print("OK — LISS-0235")
