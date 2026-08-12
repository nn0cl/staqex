"""SV-11: QPU QASM3Emitter + routing (Phase 4.1).

Note: prompt labeled this SV-09; repo already uses SV-09 for examples → SV-11 here.
"""

from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

from harness import AssertionFailure, as_main
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm import QASM3Emitter, emit_openqasm3, linear  # noqa: E402
from compiler.staqex.backend.qasm.circuit import Circuit, Gate  # noqa: E402
from compiler.staqex.backend.qasm.router import route_circuit  # noqa: E402
from compiler.staqex.cli import build_parser, cmd_run  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402

BELL = as_main("""
State q = coin()
State result = mix (q) {
  0 -> dirac(0),
  else -> dirac(1),
}
measure result
""")


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Valid OpenQASM 3 header + gates
    try:
        compiled = compile_source(BELL)
        assert compiled.unit is not None
        emitted = emit_openqasm3(compiled.unit, topology="linear", route=True)
        qasm = emitted.qasm
        if not qasm.startswith("OPENQASM 3.0"):
            raise AssertionFailure("PARSE_ERROR", qasm[:80])
        for needle in ("include \"stdgates.inc\"", "qubit[", "h q[", "cx q[", "measure"):
            if needle not in qasm:
                raise AssertionFailure("PARSE_ERROR", f"missing {needle}: {qasm}")
        # balanced brackets rough check
        if qasm.count("[") != qasm.count("]"):
            raise AssertionFailure("PARSE_ERROR", "unbalanced []")
        out.append(
            CaseResult(
                "SV-11",
                "sv11-qasm3-syntax",
                "bell → valid OpenQASM 3.0 text",
                True,
                ["QASM3Emitter"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-11",
                "sv11-qasm3-syntax",
                "QASM syntax",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # DAG/AST mapping coin→H, when-copy→CX
    try:
        compiled = compile_source(BELL)
        em = QASM3Emitter(route=False).emit_unit(compiled.unit)
        names = [g.name for g in em.circuit.gates] if em.circuit else []
        if names.count("h") < 1 or names.count("cx") < 1 or names.count("measure") != 1:
            raise AssertionFailure("PARSE_ERROR", f"gates={names}")
        out.append(
            CaseResult(
                "SV-11",
                "sv11-gate-map",
                "coin→H, when-copy→CX, measure",
                True,
                ["lower"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-11",
                "sv11-gate-map",
                "gate map",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # SWAP insertion when CX not adjacent
    try:
        # logical CX(0,2) on linear-3 needs SWAPs
        circ = Circuit(
            n_qubits=3,
            n_bits=1,
            gates=[Gate("cx", (0, 2), comment="far"), Gate("measure", (2,), bits=(0,))],
        )
        topo = linear(3)
        routed = route_circuit(circ, topo)
        swaps = [g for g in routed.gates if g.name == "swap"]
        cxs = [g for g in routed.gates if g.name == "cx"]
        if not swaps:
            raise AssertionFailure("PARSE_ERROR", f"expected SWAP, got {routed.gates}")
        if not cxs:
            raise AssertionFailure("PARSE_ERROR", "CX lost")
        # final CX must be on an edge
        a, b = cxs[-1].qubits
        if not topo.coupled(a, b):
            raise AssertionFailure("PARSE_ERROR", f"CX on non-edge {a},{b}")
        out.append(
            CaseResult(
                "SV-11",
                "sv11-swap-route",
                "linear topology inserts SWAP for distant CX",
                True,
                ["router"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-11",
                "sv11-swap-route",
                "SWAP route",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # CLI --target qpu:openqasm3 + -o
    try:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "out.qasm"
            parser = build_parser()
            args = parser.parse_args(
                ["run", "--target", "qpu:openqasm3", "-o", str(path), "-e", BELL]
            )
            err = io.StringIO()
            import contextlib

            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                code = cmd_run(args)
            if code != 0:
                raise AssertionFailure("PARSE_ERROR", err.getvalue())
            text = path.read_text(encoding="utf-8")
            if "OPENQASM 3.0" not in text or "h q[" not in text:
                raise AssertionFailure("PARSE_ERROR", text)
        out.append(
            CaseResult(
                "SV-11",
                "sv11-cli-openqasm3",
                "staqex run --target qpu:openqasm3 -o file",
                True,
                ["cli"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-11",
                "sv11-cli-openqasm3",
                "CLI openqasm3",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
