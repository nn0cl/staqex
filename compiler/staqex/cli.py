"""Staqex CLI — run / check / inspect / emit-qasm / repl / migrate (Phase 3–4)."""

from __future__ import annotations

import argparse
import functools
import json
import sys
from pathlib import Path
from typing import TextIO

from .adapters.aws_braket import (
    AwsBraketAdapter,
    BraketCredentialError,
    BraketDependencyError,
    RealAwsBraketClient,
)
from .codegen.openqasm import emit_openqasm3
from .credentials import EnvCredentialAdapter
from .format import format_source
from .ir.dag import lower_source_ast
from .live_submit import submit_live_qpu
from .migrate_unicode_math import migrate_unicode_math_source
from .pipeline import HARD_CODES, compile_path, compile_source
from .host import run_path as host_run_path, run_source as host_run_source
from .qpu_submit import ProviderJobId
from .runtime.evaluator import Evaluator
from .stdlib.io_ops import format_marginal_table
from .stdlib.prelude import PRELUDE_NAMES


def _compile_args(args: argparse.Namespace):
    """Prefer path-linked compile when a file is given (ADR 0054)."""
    if getattr(args, "expr", None):
        return compile_source(args.expr)
    if getattr(args, "file", None):
        return compile_path(args.file)
    raise SystemExit("provide a file or -e source")


def _run_args(args: argparse.Namespace, *, stdout: TextIO | None = None):
    seed = getattr(args, "seed", None)
    out = stdout if stdout is not None else sys.stdout
    workers = getattr(args, "data_parallel_workers", None)
    if workers is None:
        import os

        raw = os.environ.get("STAQEX_DATA_PARALLEL_WORKERS")
        workers = int(raw) if raw else 1
    settings = {
        "target": getattr(args, "target", "cpu"),
        "seed": seed,
        "data_parallel_workers": int(workers),
    }
    if getattr(args, "expr", None):
        return host_run_source(args.expr, settings=settings, stdout=out)
    if getattr(args, "file", None):
        return host_run_path(args.file, settings=settings, stdout=out)
    raise SystemExit("provide a file or -e source")


def _parse_target(raw: str | None) -> tuple[str, str | None]:
    """Return (family, profile) e.g. ('cpu', None), ('qpu', 'openqasm3')."""
    if raw is None or raw == "":
        return "cpu", None
    t = raw.strip().lower()
    if t in {"cpu", "local", "sim", "simulator"}:
        return "cpu", None
    if t in {"gpu", "cuda"}:
        return "gpu", None
    if t.startswith("qpu:"):
        return "qpu", t.split(":", 1)[1] or "openqasm3"
    if t == "qpu":
        return "qpu", "openqasm3"
    raise SystemExit(f"unknown --target {raw!r} (use cpu|gpu|qpu:openqasm3|qpu:<profile>)")


def cmd_run(args: argparse.Namespace) -> int:
    family, profile = _parse_target(getattr(args, "target", None))

    if getattr(args, "emit_qasm", False) or family == "qpu":
        compiled = _compile_args(args)
        if compiled.unit is None or any(d.get("code") in HARD_CODES for d in compiled.diagnostics):
            _print_diags(compiled.diagnostics)
            return 1
        topo = "linear"
        if profile and profile.startswith("grid"):
            topo = profile
        elif profile in {"linear", "grid", "grid-2x2", "grid-3x3"}:
            topo = profile
        emitted = emit_openqasm3(compiled.unit, topology=topo, route=True)
        for n in emitted.notes:
            print(f"// note: {n}", file=sys.stderr)
        if not emitted.ok:
            return 1
        text = emitted.qasm if emitted.qasm.endswith("\n") else emitted.qasm + "\n"
        out_path = getattr(args, "output", None)
        if out_path:
            Path(out_path).write_text(text, encoding="utf-8")
            print(f"// wrote {out_path}", file=sys.stderr)
        else:
            print(text, end="")
        if family == "qpu" and profile not in {None, "openqasm3", "linear", "grid", "grid-2x2", "grid-3x3"}:
            print(
                f"// qpu cloud submit reserved (profile={profile}); OpenQASM emitted locally",
                file=sys.stderr,
            )
        if family == "qpu" and not getattr(args, "also_run", False):
            return 0

    if family == "gpu":
        print(
            "gpu target reserved (Phase 4.2); falling back to cpu Joint",
            file=sys.stderr,
        )

    result = _run_args(args, stdout=sys.stdout)
    if result.status != "succeeded":
        _print_diags(list(result.diagnostics))
        return 1
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    family, profile = _parse_target(getattr(args, "target", None))
    compiled = _compile_args(args)
    diags = compiled.diagnostics
    # LISS-0199: gate on the same hard-code set as CompileResult.ok.
    hard_diags = [d for d in diags if d.get("code") in HARD_CODES]
    if family == "qpu" and compiled.unit is not None:
        dag = lower_source_ast(compiled.unit)
        coins = sum(1 for k in dag.summary()["kinds"] if k == "coin")
        if coins > 127 and profile and "eagle" in profile:
            print(
                f"TARGET_WARN: estimated logical coins={coins} may exceed profile {profile}",
                file=sys.stderr,
            )
            hard_diags.append(
                {
                    "code": "TARGET_WARN",
                    "message": f"coin-count {coins} vs profile {profile}",
                    "line": "?",
                }
            )

    if not hard_diags and compiled.unit is not None:
        print("ok — no hard compile diagnostics")
        if family != "cpu":
            print(f"target: {family}" + (f":{profile}" if profile else ""))
        if args.dag and compiled.unit is not None:
            dag = lower_source_ast(compiled.unit)
            print(f"dag nodes: {dag.summary()['node_count']}")
        return 0
    for d in hard_diags:
        code = d.get("code")
        msg = d.get("message", "")
        line = d.get("line", "?")
        fix = ""
        if code == "RETIRED_KEYWORD" and d.get("replacement"):
            fix = f"  (fix-it: use `{d['replacement']}`)"
        print(f"{code}:{line}: {msg}{fix}", file=sys.stderr)
    if compiled.unit is None:
        return 1
    return 1 if any(d.get("code") in HARD_CODES for d in hard_diags) else 0


def cmd_inspect(args: argparse.Namespace) -> int:
    compiled = _compile_args(args)
    if compiled.unit is None or any(d.get("code") in HARD_CODES for d in compiled.diagnostics):
        _print_diags(compiled.diagnostics)
        return 1
    unit = compiled.unit
    from .ast_nodes import Measure

    if unit.main is not None:
        unit.main.body.stmts = [s for s in unit.main.body.stmts if not isinstance(s, Measure)]
    buf: TextIO = sys.stdout
    ev = Evaluator(seed=args.seed, inspect_sink=buf)
    result = ev.run_unit(unit, stdout=buf)
    print("--- joint marginals ---")
    for var in result.joint.variables():
        print(format_marginal_table(result.joint.marginal(var), label=var), end="")
    if result.joint.is_vacuum():
        print("(vacuum)")
    if args.dag:
        full = _compile_args(args)
        if full.unit:
            print(lower_source_ast(full.unit).to_dot())
    return 0


def cmd_repl(args: argparse.Namespace) -> int:
    print("Staqex REPL — enter statements; blank line runs; :quit to exit")
    print(f"Prelude: {', '.join(sorted(PRELUDE_NAMES))}")
    buf: list[str] = []
    seed = args.seed
    while True:
        try:
            line = input("staqex> " if not buf else "...   ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if line.strip() in {":quit", ":exit", ":q"}:
            return 0
        if line.strip() == ":clear":
            buf.clear()
            continue
        if line.strip() == "" and buf:
            source = "\n".join(buf) + "\n"
            buf.clear()
            if "measure" not in source:
                last = None
                for ln in source.splitlines():
                    s = ln.strip()
                    if s.startswith("state "):
                        last = s.split("=")[0].replace("state", "").strip()
                if last:
                    source = source + f"measure {last}\n"
            result = host_run_source(
                source,
                settings={"target": "local", "seed": seed},
                stdout=sys.stdout,
            )
            if result.status != "succeeded":
                _print_diags(list(result.diagnostics))
            continue
        buf.append(line)


def cmd_dag(args: argparse.Namespace) -> int:
    compiled = _compile_args(args)
    if compiled.unit is None:
        _print_diags(compiled.diagnostics)
        return 1
    dag = lower_source_ast(compiled.unit)
    if args.dot:
        print(dag.to_dot(), end="")
    else:
        print(dag.summary())
    return 0


def cmd_emit_qasm(args: argparse.Namespace) -> int:
    compiled = _compile_args(args)
    if compiled.unit is None or any(d.get("code") in HARD_CODES for d in compiled.diagnostics):
        _print_diags(compiled.diagnostics)
        return 1
    emitted = emit_openqasm3(compiled.unit)
    for n in emitted.notes:
        print(f"// note: {n}", file=sys.stderr)
    if not emitted.ok:
        return 1
    out = emitted.qasm
    if getattr(args, "output", None):
        Path(args.output).write_text(out if out.endswith("\n") else out + "\n", encoding="utf-8")
    else:
        print(out, end="" if out.endswith("\n") else "\n")
    return 0


def _build_live_qpu_adapter(device_arn: str) -> AwsBraketAdapter:
    """LISS-0396: real client + env credentials, both already-shipped
    (ADR 0202/LISS-0194). Never called by this module's own test suite in
    its real (non-mocked) form except to exercise the deliberate
    fail-closed path when amazon-braket-sdk is absent (RealAwsBraketClient
    itself never touches the network on that path).
    """
    return AwsBraketAdapter(
        client=RealAwsBraketClient(),
        device_arn=device_arn,
        credentials=EnvCredentialAdapter(),
    )


def cmd_submit_live_qpu(args: argparse.Namespace) -> int:
    """LISS-0396 (ADR 0203 named CLI follow-up): wires the already-shipped
    `submit_live_qpu` entrypoint to a real `AwsBraketAdapter`. This agent
    never invokes this command against a real device (ADR 0202 Decision
    5) -- it is the human Adjudicator's own terminal, own AWS credentials,
    own explicit invocation.
    """
    if args.provider != "aws-braket":
        print(
            f"submit-live-qpu: unsupported --provider {args.provider!r} "
            "(only aws-braket is available)",
            file=sys.stderr,
        )
        return 1
    source = _load_source(args)
    execution_settings: dict[str, object] = {}
    if getattr(args, "shots", None) is not None:
        execution_settings["shots"] = args.shots
    print(
        f"submit-live-qpu: submitting to AWS Braket device {args.device_arn} "
        "-- this may incur real cost on real hardware",
        file=sys.stderr,
    )
    try:
        adapter = _build_live_qpu_adapter(args.device_arn)
        job_id, diagnostics = submit_live_qpu(
            source, adapter=adapter, execution_settings=execution_settings
        )
    except (BraketDependencyError, BraketCredentialError) as exc:
        print(f"submit-live-qpu: {exc}", file=sys.stderr)
        return 1
    if job_id is None:
        _print_diags(list(diagnostics))
        return 1
    print(f"provider={job_id.provider} id={job_id.opaque_id}")
    return 0


def _cmd_qpu_job(args: argparse.Namespace, *, action: str) -> int:
    """LISS-0397 (ADR 0203/0202 follow-up): shared dispatcher for the four
    `qpu-job-*` commands, wiring the already-shipped `QpuJobPort.status`/
    `wait`/`result`/`cancel` (all implemented, unchanged, by
    `AwsBraketAdapter`). `--device-arn` is still required to construct the
    adapter even though none of these four operations read it (disclosed
    LISS-0397 Plan wrinkle, not fixed here).
    """
    if args.provider != "aws-braket":
        print(
            f"qpu-job-{action}: unsupported --provider {args.provider!r} "
            "(only aws-braket is available)",
            file=sys.stderr,
        )
        return 1
    job_id = ProviderJobId(provider=args.provider, opaque_id=args.id)
    try:
        adapter = _build_live_qpu_adapter(args.device_arn)
        outcome = getattr(adapter, action)(job_id)
    except (BraketDependencyError, BraketCredentialError) as exc:
        print(f"qpu-job-{action}: {exc}", file=sys.stderr)
        return 1
    if action == "result":
        try:
            print(json.dumps(outcome, indent=2))
        except TypeError:
            print(outcome)
    else:
        print(outcome.value)
    return 0


def _migrate_read_source(path: Path) -> str | None:
    """Read UTF-8 source for migrate; print stderr and return None on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"migrate: cannot read {path}: {exc}", file=sys.stderr)
        return None
    except UnicodeDecodeError as exc:
        print(f"migrate: invalid UTF-8 in {path}: {exc}", file=sys.stderr)
        return None


def _migrate_write_source(path: Path, text: str) -> bool:
    """Write UTF-8 text for migrate; print stderr and return False on failure."""
    try:
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        print(f"migrate: cannot write {path}: {exc}", file=sys.stderr)
        return False
    return True


def _emit_rewritten_source(
    *,
    command: str,
    path: Path,
    rewritten: str,
    write_in_place: bool,
    out_path: str | None,
) -> int:
    """Emit rewritten text to in-place file, -o path, or stdout."""
    if write_in_place and out_path:
        print(f"{command}: --write and -o are mutually exclusive", file=sys.stderr)
        return 1
    if write_in_place:
        return 0 if _migrate_write_source(path, rewritten) else 1
    if out_path:
        return 0 if _migrate_write_source(Path(out_path), rewritten) else 1
    print(rewritten, end="")
    return 0


def _check_rewritten_source(*, command: str, path: Path, original: str, rewritten: str) -> int:
    if rewritten == original:
        return 0
    print(f"{command}: {path} would change under canonical formatting", file=sys.stderr)
    return 1


def cmd_migrate(args: argparse.Namespace) -> int:
    """Rewrite Unicode math dual-accept spellings (M-P02–M-P04) via Slice B library."""
    path = Path(args.path)
    source = _migrate_read_source(path)
    if source is None:
        return 1

    migrated = migrate_unicode_math_source(source)

    if getattr(args, "check", False):
        if migrated == source:
            return 0
        print(f"migrate: {path} would change under Unicode math migration", file=sys.stderr)
        return 1

    return _emit_rewritten_source(
        command="migrate",
        path=path,
        rewritten=migrated,
        write_in_place=bool(getattr(args, "write", False)),
        out_path=getattr(args, "output", None),
    )


def cmd_format(args: argparse.Namespace) -> int:
    """Emit the current canonical source spelling for formatter-owned slices."""
    path = Path(args.path)
    source = _migrate_read_source(path)
    if source is None:
        return 1

    formatted = format_source(source)

    if getattr(args, "check", False):
        return _check_rewritten_source(
            command="format",
            path=path,
            original=source,
            rewritten=formatted,
        )

    return _emit_rewritten_source(
        command="format",
        path=path,
        rewritten=formatted,
        write_in_place=bool(getattr(args, "write", False)),
        out_path=getattr(args, "output", None),
    )


def _load_source(args: argparse.Namespace) -> str:
    if getattr(args, "expr", None):
        return args.expr
    if getattr(args, "file", None):
        return Path(args.file).read_text(encoding="utf-8")
    raise SystemExit("provide a file or -e source")


def _print_diags(diags: list) -> None:
    for d in diags:
        print(f"{d.get('code')}: {d.get('message')}", file=sys.stderr)


def _add_target(sp: argparse.ArgumentParser) -> None:
    sp.add_argument(
        "-t",
        "--target",
        default="cpu",
        help="cpu | gpu | qpu:<profile> (ADR 0036; source stays portable)",
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="staqex", description="Staqex toolchain (Phase 3–4)")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_src(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("file", nargs="?", help=".sqx source file")
        sp.add_argument("-e", "--eval", dest="expr", help="source string")
        sp.add_argument("--seed", type=int, default=None)

    pr = sub.add_parser("run", help="compile and execute (terminal measure)")
    add_src(pr)
    _add_target(pr)
    pr.add_argument("--emit-qasm", action="store_true", help="print OpenQASM 3 sketch")
    pr.add_argument("-o", "--output", help="write OpenQASM to file (with qpu / --emit-qasm)")
    pr.add_argument(
        "--also-run",
        action="store_true",
        help="with --target qpu, also run cpu Joint after emit",
    )
    pr.add_argument(
        "--data-parallel-workers",
        type=int,
        default=None,
        help="CPU ThreadPool workers for independent Joint worlds "
        "(ADR 0159; env STAQEX_DATA_PARALLEL_WORKERS)",
    )
    pr.set_defaults(func=cmd_run)

    pc = sub.add_parser("check", help="lint Forbidden/Retired + Early Collapse")
    add_src(pc)
    _add_target(pc)
    pc.add_argument("--dag", action="store_true", help="print DAG node count if ok")
    pc.set_defaults(func=cmd_check)

    pi = sub.add_parser("inspect", help="non-destructive joint dump (no sample)")
    add_src(pi)
    pi.add_argument("--dag", action="store_true", help="also print DOT DAG")
    pi.set_defaults(func=cmd_inspect)

    pd = sub.add_parser("dag", help="lower AST to computation DAG IR")
    add_src(pd)
    pd.add_argument("--dot", action="store_true", help="emit Graphviz DOT")
    pd.set_defaults(func=cmd_dag)

    pe = sub.add_parser("emit-qasm", help="lower to OpenQASM 3 sketch (ADR 0036)")
    add_src(pe)
    pe.add_argument("-o", "--output", help="write QASM to file")
    pe.set_defaults(func=cmd_emit_qasm)

    psl = sub.add_parser(
        "submit-live-qpu",
        help="submit compiled QASM3 to a real QPU provider (ADR 0203; real cost)",
    )
    add_src(psl)
    psl.add_argument(
        "--device-arn", required=True, help="provider device identifier (e.g. AWS Braket ARN)"
    )
    psl.add_argument("--shots", type=int, default=None, help="default: adapter's own default")
    psl.add_argument(
        "--provider", default="aws-braket", help="only aws-braket is currently available"
    )
    psl.set_defaults(func=cmd_submit_live_qpu)

    def add_qpu_job_parser(name: str, action: str, help_text: str) -> None:
        pj = sub.add_parser(name, help=help_text)
        pj.add_argument("--id", required=True, help="provider opaque job id")
        pj.add_argument(
            "--device-arn",
            required=True,
            help="required to construct the adapter (unused by this operation)",
        )
        pj.add_argument(
            "--provider", default="aws-braket", help="only aws-braket is currently available"
        )
        pj.set_defaults(func=functools.partial(_cmd_qpu_job, action=action))

    add_qpu_job_parser("qpu-job-status", "status", "query a live QPU job's status")
    add_qpu_job_parser("qpu-job-wait", "wait", "wait for a live QPU job's terminal status")
    add_qpu_job_parser("qpu-job-result", "result", "fetch a live QPU job's result")
    add_qpu_job_parser("qpu-job-cancel", "cancel", "cancel a live QPU job")

    prepl = sub.add_parser("repl", help="interactive shell")
    prepl.add_argument("--seed", type=int, default=None)
    prepl.set_defaults(func=cmd_repl)

    pm = sub.add_parser(
        "migrate",
        help="rewrite ASCII Dirac/tensor/adjoint to Unicode (M-P02–M-P04 only)",
    )
    pm.add_argument("path", help=".sqx (or UTF-8 text) source file")
    pm.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="rewrite the file in place",
    )
    pm.add_argument(
        "--check",
        action="store_true",
        help="exit 0 if already migrated; exit 1 if drift",
    )
    pm.add_argument(
        "-o",
        "--output",
        help="write migrated text to PATH (mutually exclusive with --write)",
    )
    pm.set_defaults(func=cmd_migrate)

    pf = sub.add_parser(
        "format",
        help="emit canonical Unicode formatting for formatter-owned slices",
    )
    pf.add_argument("path", help=".sqx (or UTF-8 text) source file")
    pf.add_argument(
        "-w",
        "--write",
        action="store_true",
        help="rewrite the file in place",
    )
    pf.add_argument(
        "--check",
        action="store_true",
        help="exit 0 if already formatted; exit 1 if drift",
    )
    pf.add_argument(
        "-o",
        "--output",
        help="write formatted text to PATH (mutually exclusive with --write)",
    )
    pf.set_defaults(func=cmd_format)

    return p


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] not in {
        "run",
        "check",
        "inspect",
        "dag",
        "emit-qasm",
        "submit-live-qpu",
        "qpu-job-status",
        "qpu-job-wait",
        "qpu-job-result",
        "qpu-job-cancel",
        "repl",
        "migrate",
        "format",
        "-h",
        "--help",
    }:
        argv = ["run", *argv]
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
