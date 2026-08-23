"""SV-10: Backend targets (ADR 0036) — portable source + OpenQASM emit."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure, as_main
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import cmd_emit_qasm, cmd_run, build_parser  # noqa: E402
from compiler.staqex.codegen.openqasm import emit_openqasm3  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


PORTABLE = as_main("""
State q = Coin()
State result = Mix (q) {
  0 -> Dirac(0),
  else -> Dirac(1),
}
Measure result
""")


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Coin/Mix remains ideal mixture meaning; static QASM rejects it.
    try:
        compiled = compile_source(PORTABLE)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        emitted = emit_openqasm3(compiled.unit)
        if emitted.ok:
            raise AssertionFailure("PARSE_ERROR", "Coin/Mix must not emit a unitary fallback")
        if emitted.qasm:
            raise AssertionFailure("PARSE_ERROR", emitted.qasm)
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
                "SV-10",
                "sv10-openqasm-bell",
                "Coin/Mix → explicit capability rejection",
                True,
                ["emit_openqasm3"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-10",
                "sv10-openqasm-bell",
                "OpenQASM emit",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # CLI emit-qasm
    try:
        parser = build_parser()
        args = parser.parse_args(["emit-qasm", "-e", PORTABLE])
        buf = io.StringIO()
        err = io.StringIO()
        import contextlib

        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            code = cmd_emit_qasm(args)
        if code != 1:
            raise AssertionFailure("PARSE_ERROR", f"exit={code}: {err.getvalue()}")
        if buf.getvalue() or "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE" not in err.getvalue():
            raise AssertionFailure("PARSE_ERROR", f"stdout={buf.getvalue()} stderr={err.getvalue()}")
        out.append(
            CaseResult(
                "SV-10",
                "sv10-cli-emit-qasm",
                "staqex emit-qasm CLI",
                True,
                ["cli"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-10",
                "sv10-cli-emit-qasm",
                "emit-qasm CLI",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # --target cpu still runs Joint
    try:
        parser = build_parser()
        args = parser.parse_args(["run", "--target", "cpu", "--seed", "0", "-e", PORTABLE])
        buf = io.StringIO()
        err = io.StringIO()
        import contextlib

        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            code = cmd_run(args)
        if code != 0:
            raise AssertionFailure("PARSE_ERROR", err.getvalue())
        out.append(
            CaseResult(
                "SV-10",
                "sv10-target-cpu",
                "staqex run --target cpu",
                True,
                ["--target cpu"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-10",
                "sv10-target-cpu",
                "--target cpu",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # --target qpu emits QASM without requiring vendor import in source
    try:
        parser = build_parser()
        args = parser.parse_args(["run", "--target", "qpu:ibm_eagle", "-e", PORTABLE])
        buf = io.StringIO()
        err = io.StringIO()
        import contextlib

        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(err):
            code = cmd_run(args)
        if code != 1:
            raise AssertionFailure("PARSE_ERROR", f"exit={code}: {err.getvalue()}")
        if buf.getvalue() or "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE" not in err.getvalue():
            raise AssertionFailure("PARSE_ERROR", f"stdout={buf.getvalue()} stderr={err.getvalue()}")
        if "import" in PORTABLE and "backend" in PORTABLE:
            raise AssertionFailure("FORBIDDEN_KEYWORD", "source must stay portable")
        out.append(
            CaseResult(
                "SV-10",
                "sv10-target-qpu-emit",
                "staqex run --target qpu:* rejects unsupported Coin/Mix projection",
                True,
                ["--target qpu"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-10",
                "sv10-target-qpu-emit",
                "--target qpu",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Docs present
    try:
        for rel in (
            "docs/architecture/decision-themes/dec-0006-host-qpu-and-external-ports.md",
            "docs/architecture/staqex-backend-targets.md",
            "examples/applied/A08_entangled_compute_ancilla/main_entangled_compute_ancilla.sqx",
        ):
            if not (_REPO / rel).is_file():
                raise AssertionFailure("PARSE_ERROR", f"missing {rel}")
        out.append(
            CaseResult(
                "SV-10",
                "sv10-docs",
                "ADR 0036 + portable_bell_qpu.sqx",
                True,
                ["docs"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-10",
                "sv10-docs",
                "docs",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
