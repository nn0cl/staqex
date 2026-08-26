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
State q = Coin()
State result = Mix (q) {
  0 -> Dirac(0),
  else -> Dirac(1),
}
Measure result
""")


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Coin/Mix has no static finite projection; it must reject atomically.
    try:
        compiled = compile_source(BELL)
        assert compiled.unit is not None
        emitted = emit_openqasm3(compiled.unit, topology="linear", route=True)
        if emitted.ok or emitted.qasm:
            raise AssertionFailure("PARSE_ERROR", "Coin/Mix emitted QASM")
        if emitted.circuit is None:
            raise AssertionFailure("PARSE_ERROR", "missing rejection circuit")
        if emitted.circuit.reject_code != "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE":
            raise AssertionFailure("PARSE_ERROR", str(emitted.circuit.reject_code))
        if emitted.circuit.provenance is None:
            raise AssertionFailure("PARSE_ERROR", "missing rejection provenance")
        if emitted.circuit.provenance.get("reason") != "mixture_projection_unavailable":
            raise AssertionFailure("PARSE_ERROR", str(emitted.circuit.provenance))
        if emitted.circuit.gates or emitted.circuit.allocation_started:
            raise AssertionFailure("PARSE_ERROR", "rejection retained target artifacts")
        out.append(
            CaseResult(
                "SV-11",
                "sv11-qasm3-syntax",
                "Coin/Mix → explicit capability rejection",
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

    # The QASM consumer must not use the retired AST gate mapping for Coin/Mix.
    try:
        compiled = compile_source(BELL)
        em = QASM3Emitter(route=False).emit_unit(compiled.unit)
        if em.ok or em.qasm or em.circuit is None:
            raise AssertionFailure("PARSE_ERROR", "Coin/Mix emitted a gate fallback")
        if em.circuit.reject_code != "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE":
            raise AssertionFailure("PARSE_ERROR", str(em.circuit.reject_code))
        if em.circuit.provenance is None or em.circuit.provenance.get("reason") != "mixture_projection_unavailable":
            raise AssertionFailure("PARSE_ERROR", str(em.circuit.provenance))
        if em.circuit.gates or em.circuit.allocation_started:
            raise AssertionFailure("PARSE_ERROR", "rejection retained target artifacts")
        out.append(
            CaseResult(
                "SV-11",
                "sv11-gate-map",
                "Coin/Mix does not use the retired gate fallback",
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
            if code != 1:
                raise AssertionFailure("PARSE_ERROR", err.getvalue())
            text = path.read_text(encoding="utf-8") if path.exists() else ""
            if text or path.exists() or "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE" not in err.getvalue():
                raise AssertionFailure("PARSE_ERROR", f"file={text} stderr={err.getvalue()}")
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
