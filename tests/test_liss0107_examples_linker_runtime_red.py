"""LISS-0107 Phase 1 Red — linked module Operator factory runtime gaps.

Official multi-file examples compile after ADR 0054 linking, but several fail at
runtime when a library ``fn`` returns an ``Operator`` bound to a local name.
Minimal two-file fixtures isolate the defect without masking it in example
source.

Expected Red failures before Phase 2 Green:
- ``unbound Operator / scalar `Coin`` (factory return not resolved in caller env)
- ``RecursionError`` in ``op_space`` (self-referential Operator env for ``H``)
"""

from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_path  # noqa: E402

_OFFICIAL_MULTIFILE_ENTRIES = (
    (
        "SV-09/sv09-basics-B09-main_multi_file_modules",
        "examples/basics/B09_multi_file_modules/main_multi_file_modules.sqx",
    ),
    (
        "SV-09/sv09-applied-A06-main_topological_edge_memory",
        "examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx",
    ),
    (
        "SV-09/sv09-applied-A02-main_robot_graph_planner",
        "examples/applied/A02_robot_graph_planner/main_robot_graph_planner.sqx",
    ),
    (
        "SV-09/sv09-applied-A10-main_mission_observatory",
        "examples/applied/A10_mission_observatory/main_mission_observatory.sqx",
    ),
    (
        "SV-31/sv31-linked-run",
        "examples/basics/B09_multi_file_modules/main_multi_file_modules.sqx",
    ),
)


def _run_entry(path: Path) -> None:
    result = run_path(path, seed=0, stdout=io.StringIO())
    if not result.compile_ok:
        raise AssertionError(f"compile failed: {result.diagnostics}")
    if result.eval.measure is None and not result.eval.joint.is_vacuum():
        raise AssertionError("missing terminal measurement")


def _write_linked_fixture(
    tmp: Path,
    *,
    lib_package: str,
    lib_stem: str,
    lib_body: str,
    main_source: str,
) -> Path:
    lib = f"package {lib_package}\n\n{lib_body.strip()}\n"
    (tmp / f"{lib_stem}.sqx").write_text(lib, encoding="utf-8")
    main = tmp / "main.sqx"
    main.write_text(main_source, encoding="utf-8")
    return main


def test_linked_operator_factory_result_is_resolved_at_runtime() -> None:
    """Library fn ``return Coin`` must lower to a closed OpExpr in the caller."""
    lib_body = """
pub fn make_op() -> Operator {
    Operator Coin = (X + Z) * inv_sqrt2
    return Coin
}
"""
    main = """
package com.staqex.tests.liss0107.coin_main

import com.staqex.tests.liss0107.coinlib

pub fn main() -> Unit {
    Operator k = make_op()
    State<Qubit> c = |+>
    state c2 = apply(k, c)
    measure c2
}
"""
    with tempfile.TemporaryDirectory() as td:
        entry = _write_linked_fixture(
            Path(td),
            lib_package="com.staqex.tests.liss0107.coinlib",
            lib_stem="coinlib",
            lib_body=lib_body,
            main_source=main,
        )
        _run_entry(entry)


def test_linked_hamiltonian_factory_op_space_terminates() -> None:
    """Returned Hamiltonian locals must not leave self-referential ``op_env``."""
    lib_body = """
pub fn build_h() -> Operator {
    Operator H = 1.0545718e-19 * (hop(0, 1) + hop(1, 0))
    return H
}
"""
    main = """
package com.staqex.tests.liss0107.hop_main

import com.staqex.tests.liss0107.hoplib

pub fn main() -> Unit {
    Operator H = build_h()
    State<Position> psi = dirac(0)
    state psi = evolve { psi under H for 0.1.fs }.run()
    measure psi
}
"""
    with tempfile.TemporaryDirectory() as td:
        entry = _write_linked_fixture(
            Path(td),
            lib_package="com.staqex.tests.liss0107.hoplib",
            lib_stem="hoplib",
            lib_body=lib_body,
            main_source=main,
        )
        _run_entry(entry)


def test_official_multifile_examples_run_without_runtime_errors() -> None:
    """Regression over all SV-09 / SV-31 linked official entries (LISS-0107)."""
    failures: list[str] = []

    for case_id, relative_path in _OFFICIAL_MULTIFILE_ENTRIES:
        path = _REPO / relative_path
        try:
            _run_entry(path)
        except Exception as exc:  # noqa: BLE001 — surface current runtime defect
            failures.append(f"{case_id}: {type(exc).__name__}: {exc}")

    assert not failures, "LISS-0107 official linked runtime Red cases:\n" + "\n".join(
        failures
    )


if __name__ == "__main__":
    test_linked_operator_factory_result_is_resolved_at_runtime()
    test_linked_hamiltonian_factory_op_space_terminates()
    test_official_multifile_examples_run_without_runtime_errors()
    print("OK — LISS-0107 linked runtime cases")
