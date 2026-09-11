#!/usr/bin/env python3
"""Capture deterministic public/API and representative behavior evidence."""

from __future__ import annotations

import argparse
from dataclasses import asdict, is_dataclass
import hashlib
import importlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import tomllib
from typing import Any, Mapping


def _jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return _jsonable(asdict(value))
    if isinstance(value, Mapping):
        return {
            str(key): _jsonable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted((_jsonable(item) for item in value), key=repr)
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, float) and not math.isfinite(value):
        return repr(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return repr(value)


def _canonical(value: Any) -> str:
    return json.dumps(_jsonable(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _evidence(kind: str, status: str, payload: Any) -> dict[str, Any]:
    normalized = _jsonable(payload)
    digest = hashlib.sha256(_canonical(normalized).encode("utf-8")).hexdigest()
    return {
        "kind": kind,
        "status": status,
        "sha256": f"sha256:{digest}",
        "evidence": normalized,
    }


def _source_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise ValueError(f"case input escapes repository: {relative}") from error
    if not path.is_file():
        raise FileNotFoundError(relative)
    return path


def _public_symbols(module_name: str) -> list[str]:
    module = importlib.import_module(module_name)
    declared = getattr(module, "__all__", None)
    if declared is not None:
        return sorted(str(name) for name in declared)
    # Without __all__, Python's public wildcard-import surface is every name
    # that does not start with an underscore. Imported names may be accidental,
    # but they are still reachable through the existing module path and must be
    # visible to a compatibility-preserving decomposition review.
    return sorted(name for name in vars(module) if not name.startswith("_"))


def _runtime_case(root: Path, case: Mapping[str, Any]) -> dict[str, Any]:
    from compiler.staqex.host import run_path

    source = _source_path(root, str(case["source"]))
    output = io.StringIO()
    result = run_path(
        str(source), settings={"seed": int(case.get("seed", 0))}, stdout=output
    )
    payload = {
        "stdout": output.getvalue(),
        "measurements": result.measurements,
        "diagnostics": result.diagnostics,
        "metadata": result.metadata,
    }
    status = "accepted" if result.status == "succeeded" else "rejected"
    return _evidence("runtime", status, payload)


def _qasm_case(root: Path, case: Mapping[str, Any]) -> dict[str, Any]:
    from compiler.staqex.codegen_qasm import StaqexCompiler

    source = _source_path(root, str(case["source"]))
    try:
        qasm = StaqexCompiler().compile_to_qasm3(str(source))
    except (OSError, RuntimeError, ValueError) as error:
        return _evidence("qasm", "rejected", {"error": str(error).replace(str(root), "<root>")})
    return _evidence("qasm", "accepted", {"qasm": qasm})


def _diagnostic_case(root: Path, case: Mapping[str, Any]) -> dict[str, Any]:
    from compiler.staqex.pipeline import compile_path

    source = _source_path(root, str(case["source"]))
    compiled = compile_path(source)
    payload = {
        "compile_ok": compiled.ok,
        "diagnostics": compiled.diagnostics,
    }
    return _evidence("diagnostic", "accepted" if compiled.ok else "rejected", payload)


def _load_cases(path: Path) -> dict[str, Any]:
    document = tomllib.loads(path.read_text(encoding="utf-8"))
    if document.get("version") != 1:
        raise ValueError("unsupported baseline case version")
    return document


def build_baseline(root: Path, cases_path: Path) -> dict[str, Any]:
    root_text = str(root)
    if root_text not in sys.path:
        sys.path.insert(0, root_text)
    cases = _load_cases(cases_path)
    all_cases: list[tuple[str, Mapping[str, Any]]] = []
    for family in ("runtime_case", "qasm_case", "diagnostic_case"):
        for case in cases.get(family, []):
            _source_path(root, str(case["source"]))
            all_cases.append((family, case))

    public_modules = {
        str(name): _public_symbols(str(name))
        for name in cases.get("public_modules", [])
    }
    evidence: dict[str, Any] = {}
    builders = {
        "runtime_case": _runtime_case,
        "qasm_case": _qasm_case,
        "diagnostic_case": _diagnostic_case,
    }
    for family, case in all_cases:
        case_id = str(case["id"])
        if case_id in evidence:
            raise ValueError(f"duplicate case id: {case_id}")
        evidence[case_id] = builders[family](root, case)
    return {
        "schema_version": 1,
        "public_modules": public_modules,
        "cases": evidence,
    }


def _write_atomic(path: Path, document: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            handle.write(rendered)
            temporary = Path(handle.name)
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        document = build_baseline(root, args.cases.resolve())
        _write_atomic(args.output.resolve(), document)
    except FileNotFoundError as error:
        print(f"REFACTOR_BASELINE_INPUT_MISSING: {error}")
        return 1
    except (ImportError, OSError, TypeError, ValueError, tomllib.TOMLDecodeError) as error:
        print(f"REFACTOR_BASELINE_INVALID: {error}")
        return 1
    print(f"REFACTOR_BASELINE_OK cases={len(document['cases'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
