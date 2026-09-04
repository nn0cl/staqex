"""Compile + run Staqex source on the Discrete PMF Kernel."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TextIO

from .finite_binder import identity_acting_space_diagnostics
from .pipeline import HARD_CODES, compile_path, compile_source
from .resource_enforcement import enforce_optional_budget
from .resource_profile import ResourceProfile, SimulationResourceEstimate
from .runtime.evaluator import EvalResult, Evaluator
from .runtime.joint import Joint


@dataclass
class RunResult:
    eval: EvalResult
    diagnostics: list[dict[str, Any]]
    compile_ok: bool

    @property
    def ok(self) -> bool:
        """Compatibility alias used by representative-program Red suites."""
        return self.compile_ok

    @property
    def measurements(self) -> tuple[Any, ...]:
        """Compatibility alias: terminal measure payload for deterministic checks."""
        if self.eval.measure is None:
            return ()
        return (self.eval.measure,)


def run_source(
    source: str,
    *,
    seed: int | None = None,
    stdout: TextIO | None = None,
    require_clean: bool = True,
    resource_profile: ResourceProfile | None = None,
    resource_estimate: SimulationResourceEstimate | None = None,
    data_parallel_workers: int = 1,
) -> RunResult:
    compiled = compile_source(source)
    compiled.diagnostics.extend(
        identity_acting_space_diagnostics(compiled.unit) if compiled.unit else []
    )
    has_hard = any(d.get("code") in HARD_CODES for d in compiled.diagnostics)
    if (require_clean and has_hard) or compiled.unit is None:
        return RunResult(
            eval=EvalResult(joint=Joint.empty()),
            diagnostics=compiled.diagnostics,
            compile_ok=False,
        )

    diagnostics = list(compiled.diagnostics)
    decision = enforce_optional_budget(
        resource_profile,
        resource_estimate,
        lane="simulator",
    )
    if decision is not None:
        diagnostics.extend(decision.diagnostics)
        if not decision.continue_execution:
            return RunResult(
                eval=EvalResult(joint=Joint.empty()),
                diagnostics=diagnostics,
                compile_ok=False,
            )

    ev = Evaluator(
        seed=seed,
        grid_hamiltonians=dict(compiled.grid_hamiltonians or {}),
        data_parallel_workers=data_parallel_workers,
    )
    out = stdout if stdout is not None else sys.stdout
    result = ev.run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=out,
    )
    return RunResult(eval=result, diagnostics=diagnostics, compile_ok=True)


def run_path(
    entry: str | Path,
    *,
    seed: int | None = None,
    stdout: TextIO | None = None,
    require_clean: bool = True,
    data_parallel_workers: int = 1,
) -> RunResult:
    """Compile+run an entry file with ADR 0054 module linking."""
    compiled = compile_path(entry)
    compiled.diagnostics.extend(
        identity_acting_space_diagnostics(compiled.unit) if compiled.unit else []
    )
    has_hard = any(d.get("code") in HARD_CODES for d in compiled.diagnostics)
    if (require_clean and has_hard) or compiled.unit is None:
        return RunResult(
            eval=EvalResult(joint=Joint.empty()),
            diagnostics=compiled.diagnostics,
            compile_ok=False,
        )

    ev = Evaluator(
        seed=seed,
        grid_hamiltonians=dict(compiled.grid_hamiltonians or {}),
        data_parallel_workers=data_parallel_workers,
    )
    out = stdout if stdout is not None else sys.stdout
    result = ev.run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=out,
    )
    return RunResult(eval=result, diagnostics=compiled.diagnostics, compile_ok=True)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="staqex", description="Staqex Kernel runner (Phase 2.2)")
    p.add_argument("file", nargs="?", help="Source .sqx file")
    p.add_argument("-e", "--eval", dest="expr", help="Run source string")
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args(argv)

    if args.expr:
        result = run_source(args.expr, seed=args.seed, stdout=sys.stdout)
    elif args.file:
        result = run_path(args.file, seed=args.seed, stdout=sys.stdout)
    else:
        p.error("provide a file or -e source")

    if not result.compile_ok:
        for d in result.diagnostics:
            print(f"{d.get('code')}: {d.get('message')}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
