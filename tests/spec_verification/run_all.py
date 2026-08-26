#!/usr/bin/env python3
"""Run all Staqex Spec Verification suites and emit compliance report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from harness.report import CaseResult, SuiteReport  # noqa: E402
from suites import (  # noqa: E402
    sv01_lifting,
    sv02_when,
    sv03_failure_superposition,
    sv04_early_collapse,
    sv05_vacuum_compare,
    sv06_package_vocab,
    sv07_kernel_eval,
    sv08_ecosystem,
    sv09_examples,
    sv10_backend_targets,
    sv11_qasm_transpilation,
    sv13_physical_syntax,
    sv14_complex_phase_interference,
    sv15_type_first_dimensions,
    sv16_structured_program_syntax,
    sv17_quantum_mechanics_syntax,
    sv18_physical_axioms,
    sv19_arbitrary_hamiltonian,
    sv20_dtqw_apply,
    sv21_capply,
    sv22_typed_product,
    sv23_unitarity,
    sv24_multi_capply,
    sv25_open_control,
    sv26_mixed_control,
    sv27_fock_quadrature,
    sv28_sparse_pauli,
    sv29_position_grid_ho,
    sv30_extended_unitarity,
    sv31_module_linker,
)

_SUITE_MODULES = (
    sv01_lifting,
    sv02_when,
    sv03_failure_superposition,
    sv04_early_collapse,
    sv05_vacuum_compare,
    sv06_package_vocab,
    sv07_kernel_eval,
    sv08_ecosystem,
    sv09_examples,
    sv10_backend_targets,
    sv11_qasm_transpilation,
    sv13_physical_syntax,
    sv14_complex_phase_interference,
    sv15_type_first_dimensions,
    sv16_structured_program_syntax,
    sv17_quantum_mechanics_syntax,
    sv18_physical_axioms,
    sv19_arbitrary_hamiltonian,
    sv20_dtqw_apply,
    sv21_capply,
    sv22_typed_product,
    sv23_unitarity,
    sv24_multi_capply,
    sv25_open_control,
    sv26_mixed_control,
    sv27_fock_quadrature,
    sv28_sparse_pauli,
    sv29_position_grid_ho,
    sv30_extended_unitarity,
    sv31_module_linker,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Staqex Spec Verification runner")
    parser.add_argument(
        "--write-report",
        action="store_true",
        help="write tests/spec_verification/reports/latest.{json,md}",
    )
    return parser.parse_args(argv)


def _resolve_report_module() -> ModuleType:
    """Return harness.report, preferring the package path tests may patch."""
    packaged = sys.modules.get("tests.spec_verification.harness.report")
    if packaged is not None:
        return packaged
    script_local = sys.modules.get("harness.report")
    if script_local is not None:
        return script_local
    try:
        from tests.spec_verification.harness import report as report_mod
    except ImportError:
        from harness import report as report_mod
    return report_mod


def emit_reports_if_requested(
    report: SuiteReport,
    root: Path,
    *,
    write: bool,
) -> tuple[Path, Path] | None:
    """Write compliance reports only when explicitly requested (CI / --write-report)."""
    if not write:
        return None
    return _resolve_report_module().write_reports(report, root / "reports")


def _print_run_summary(
    report: SuiteReport,
    paths: tuple[Path, Path] | None,
) -> None:
    print("=== Staqex Spec Verification ===")
    print("Protocol: docs/testing/staqex-spec-verification-protocol.md")
    for r in report.results:
        mark = "PASS" if r.passed else "FAIL"
        extra = f" [{r.error_code}] {r.message}" if not r.passed else ""
        print(f"  [{mark}] {r.suite}/{r.case_id}: {r.title}{extra}")
    print("---")
    print(f"Spec Compliance Rate: {report.compliance_rate:.2f}%  ({report.passed}/{report.total})")
    print(f"Gate: {'PASS' if report.failed == 0 else 'FAIL'}")
    if paths is None:
        print("Report: (not written; pass --write-report to emit latest.json/md)")
        return
    json_path, md_path = paths
    print(f"Report: {json_path}")
    print(f"Report: {md_path}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    results = []
    for mod in _SUITE_MODULES:
        try:
            results.extend(mod.run())
        except Exception as exc:  # noqa: BLE001 -- one suite's crash must not
            # hide every other suite's report (an uncaught runtime exception
            # in a single case is itself the failure signal, not a reason to
            # abort the whole compliance run).
            results.append(
                CaseResult(
                    suite=mod.__name__.rsplit(".", 1)[-1],
                    case_id="suite-crash",
                    title=f"{mod.__name__} raised before producing results",
                    passed=False,
                    error_code=type(exc).__name__,
                    message=str(exc),
                )
            )

    report = SuiteReport(results=results)
    paths = emit_reports_if_requested(report, ROOT, write=args.write_report)
    _print_run_summary(report, paths)
    return 0 if report.failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
