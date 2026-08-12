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
State q = coin()
State result = mix (q) {
  0 -> dirac(0),
  else -> dirac(1),
}
measure result
""")


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Pattern → H + CX + measure
    try:
        compiled = compile_source(PORTABLE)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        emitted = emit_openqasm3(compiled.unit)
        qasm = emitted.qasm
        for needle in ("OPENQASM 3.0", "h q[0]", "cx q[0], q[1]", "measure"):
            if needle not in qasm:
                raise AssertionFailure("PARSE_ERROR", f"missing {needle!r} in {qasm}")
        out.append(
            CaseResult(
                "SV-10",
                "sv10-openqasm-bell",
                "coin/when/measure → OpenQASM H+CX",
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
        if code != 0:
            raise AssertionFailure("PARSE_ERROR", err.getvalue())
        if "h q[0]" not in buf.getvalue():
            raise AssertionFailure("PARSE_ERROR", buf.getvalue())
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
        if code != 0:
            raise AssertionFailure("PARSE_ERROR", err.getvalue())
        if "OPENQASM 3.0" not in buf.getvalue():
            raise AssertionFailure("PARSE_ERROR", buf.getvalue())
        if "import" in PORTABLE and "backend" in PORTABLE:
            raise AssertionFailure("FORBIDDEN_KEYWORD", "source must stay portable")
        out.append(
            CaseResult(
                "SV-10",
                "sv10-target-qpu-emit",
                "staqex run --target qpu:* emits QASM; source portable",
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
