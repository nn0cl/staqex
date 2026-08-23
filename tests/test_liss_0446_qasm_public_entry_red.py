"""LISS-0446 / WP-0109 — public QASM ownership Red contract."""

from __future__ import annotations

from pathlib import Path
import sys
import argparse

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import compiler.staqex.backend.qasm.emitter as emitter_module
import compiler.staqex.cli as cli_module
import compiler.staqex.codegen_qasm as codegen_qasm_module
import compiler.staqex.codegen.openqasm as openqasm_module
from compiler.staqex.backend.qasm import emit_openqasm3
from compiler.staqex.codegen_qasm import OpenQASM3Generator
from compiler.staqex.pipeline import compile_path, compile_source


SPEC = REPO / "docs/specs/staqex-qasm-public-entry-canonical-sharing.md"


def _source() -> str:
    return """
    package t
    pub fn main() -> Unit {
        State q = |0>
        State q = apply(H, q)
        Measure q
    }
    """


def test_public_inventory_covers_all_local_qasm_entry_families() -> None:
    text = SPEC.read_text(encoding="utf-8")
    for required in (
        "QASM3Emitter.emit_unit",
        "emit_openqasm3",
        "OpenQASM3Generator.generate_detailed",
        "generate_from_source",
        "StaqexCompiler.compile_to_qasm3",
        "cmd_run",
        "cmd_emit_qasm",
        "emit_dynamic_qpu_qasm3",
        "emit_ch0",
        "live_submit",
    ):
        assert required in text


def test_backend_public_wrapper_consumes_compile_owned_ir(monkeypatch) -> None:
    compiled = compile_source(_source())
    assert compiled.ok, compiled.diagnostics

    def fail_rebuild(*_args, **_kwargs):
        raise AssertionError("backend wrapper must not rebuild supplied semantic IR")

    monkeypatch.setattr(emitter_module, "build_scientific_semantic_ir", fail_rebuild)
    seen = []
    original_build = emitter_module.build_qpu_ir

    def capture_build(unit, semantic_ir=None):
        seen.append(semantic_ir)
        return original_build(unit, semantic_ir)

    monkeypatch.setattr(emitter_module, "build_qpu_ir", capture_build)
    emitted = emit_openqasm3(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        route=False,
    )

    assert emitted.ok, emitted.notes
    assert "h q[0]" in emitted.qasm
    assert seen == [compiled.scientific_semantic_ir]


def test_codegen_facade_forwards_compile_owned_ir(monkeypatch) -> None:
    compiled = compile_source(_source())
    assert compiled.ok, compiled.diagnostics

    def fail_rebuild(*_args, **_kwargs):
        raise AssertionError("codegen facade must not rebuild supplied semantic IR")

    monkeypatch.setattr(emitter_module, "build_scientific_semantic_ir", fail_rebuild)
    seen = []
    original_build = emitter_module.build_qpu_ir

    def capture_build(unit, semantic_ir=None):
        seen.append(semantic_ir)
        return original_build(unit, semantic_ir)

    monkeypatch.setattr(emitter_module, "build_qpu_ir", capture_build)
    emitted = OpenQASM3Generator(route=False).generate_detailed(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
    )

    assert emitted.ok, emitted.notes
    assert "measure" in emitted.qasm
    assert seen == [compiled.scientific_semantic_ir]


def test_all_unit_facades_preserve_compile_owned_ir_identity(monkeypatch) -> None:
    compiled = compile_source(_source())
    assert compiled.ok, compiled.diagnostics
    seen = []
    original_build = emitter_module.build_qpu_ir

    def capture_build(unit, semantic_ir=None):
        seen.append(semantic_ir)
        return original_build(unit, semantic_ir)

    monkeypatch.setattr(emitter_module, "build_qpu_ir", capture_build)
    generator = OpenQASM3Generator(route=False)
    assert generator.generate(compiled.unit, semantic_ir=compiled.scientific_semantic_ir)
    assert openqasm_module.emit_openqasm3(
        compiled.unit, semantic_ir=compiled.scientific_semantic_ir, route=False
    ).ok
    assert codegen_qasm_module.generate_openqasm3(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        route=False,
    )
    assert seen == [compiled.scientific_semantic_ir] * 3


def test_cli_entries_forward_compile_owned_ir(monkeypatch, capsys) -> None:
    compiled = compile_source(_source())
    assert compiled.ok, compiled.diagnostics
    seen = []
    original_emit = cli_module.emit_openqasm3

    def capture_emit(unit, **kwargs):
        seen.append(kwargs.get("semantic_ir"))
        return original_emit(unit, **kwargs)

    monkeypatch.setattr(cli_module, "_compile_args", lambda _args: compiled)
    monkeypatch.setattr(cli_module, "emit_openqasm3", capture_emit)
    assert cli_module.cmd_emit_qasm(argparse.Namespace(output=None)) == 0
    assert cli_module.cmd_run(
        argparse.Namespace(
            target="qpu:openqasm3",
            emit_qasm=False,
            expr=None,
            file="ignored.sqx",
            output=None,
            also_run=False,
            dot=False,
        )
    ) == 0
    assert seen == [compiled.scientific_semantic_ir] * 2
    capsys.readouterr()


def test_cli_compile_paths_compile_once_before_emission(monkeypatch, capsys, tmp_path) -> None:
    compiled = compile_source(_source())
    assert compiled.ok, compiled.diagnostics
    compile_calls = []
    original_compile_source = cli_module.compile_source
    original_compile_path = cli_module.compile_path

    monkeypatch.setattr(
        cli_module,
        "compile_source",
        lambda source: (compile_calls.append("source") or original_compile_source(source)),
    )
    monkeypatch.setattr(
        cli_module,
        "compile_path",
        lambda path: (compile_calls.append("path") or original_compile_path(path)),
    )
    monkeypatch.setattr(cli_module, "emit_openqasm3", lambda unit, **kwargs: emit_openqasm3(
        unit, **kwargs
    ))
    source_args = argparse.Namespace(
        target="qpu:openqasm3",
        emit_qasm=False,
        expr=_source(),
        file=None,
        output=None,
        also_run=False,
        dot=False,
    )
    assert cli_module.cmd_run(source_args) == 0
    assert compile_calls == ["source"]
    source_path = tmp_path / "program.sqx"
    source_path.write_text(_source(), encoding="utf-8")
    compile_calls.clear()
    path_args = argparse.Namespace(
        target="qpu:openqasm3",
        emit_qasm=False,
        expr=None,
        file=str(source_path),
        output=None,
        also_run=False,
        dot=False,
    )
    assert cli_module.cmd_emit_qasm(path_args) == 0
    assert compile_calls == ["path"]
    compile_calls.clear()
    assert cli_module.cmd_run(path_args) == 0
    assert compile_calls == ["path"]
    capsys.readouterr()


def test_source_facade_compiles_once_and_forwards_that_projection(monkeypatch) -> None:
    compile_calls = 0
    original_compile = codegen_qasm_module.compile_source

    def count_compile(source: str):
        nonlocal compile_calls
        compile_calls += 1
        return original_compile(source)

    monkeypatch.setattr(codegen_qasm_module, "compile_source", count_compile)
    monkeypatch.setattr(
        emitter_module,
        "build_scientific_semantic_ir",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("source facade must forward its compile-owned IR")
        ),
    )

    emitted = OpenQASM3Generator(route=False).generate_from_source(_source())

    assert compile_calls == 1
    assert "OPENQASM 3.0;" in emitted


def test_path_facade_compiles_once_and_forwards_that_projection(monkeypatch, tmp_path) -> None:
    source_path = tmp_path / "program.sqx"
    source_path.write_text(_source(), encoding="utf-8")
    compile_calls = 0
    original_compile = codegen_qasm_module.compile_path

    def count_compile(path):
        nonlocal compile_calls
        compile_calls += 1
        return original_compile(path)

    monkeypatch.setattr(codegen_qasm_module, "compile_path", count_compile)
    monkeypatch.setattr(
        emitter_module,
        "build_scientific_semantic_ir",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("path facade must forward its compile-owned IR")
        ),
    )

    emitted = codegen_qasm_module.StaqexCompiler(route=False).compile_to_qasm3(
        str(source_path)
    )

    assert compile_calls == 1
    assert "OPENQASM 3.0;" in emitted


def test_mismatched_unit_and_semantic_ir_reject_explicitly() -> None:
    first = compile_source(_source())
    second = compile_source(
        _source().replace("apply(H, q)", "apply(X, q)")
    )
    assert first.ok and second.ok

    emitted = emit_openqasm3(
        first.unit,
        semantic_ir=second.scientific_semantic_ir,
        route=False,
    )

    assert not emitted.ok
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROVENANCE"
    assert emitted.qasm == ""
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False
    assert emitted.circuit.allocated_qubits == ()
    assert emitted.circuit.partial_program is None


def test_unit_only_compatibility_builds_at_most_once(monkeypatch) -> None:
    compiled = compile_source(_source())
    assert compiled.ok, compiled.diagnostics
    calls = 0
    original = emitter_module.build_scientific_semantic_ir

    def count_build(unit):
        nonlocal calls
        calls += 1
        return original(unit)

    monkeypatch.setattr(emitter_module, "build_scientific_semantic_ir", count_build)
    emitted = OpenQASM3Generator(route=False).generate_detailed(compiled.unit)

    assert emitted.ok, emitted.notes
    assert calls == 1


def test_acceptance_matrix_mentions_state_and_artifact_boundaries() -> None:
    text = SPEC.read_text(encoding="utf-8")
    for required in (
        "terminal `Measure`",
        "bare `Limit`",
        "explicit `Realize`",
        "no partial executable artifact",
        "mismatched unit and supplied IR",
    ):
        assert required in text


def test_qasm_entry_preserves_limit_rejection_without_artifacts() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Operator H = X
        Time duration = 0.6.fs
        Operator bare = Limit N -> Infinity {
            (I - i * H * duration / (N * hbar)) ^ N
        }
        State psi = |0>
        State result = Evolve() { bare * psi }.run()
        Measure result
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None
    emitted = emit_openqasm3(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        route=False,
    )
    assert not emitted.ok
    assert emitted.qasm == ""
    assert emitted.circuit is not None
    assert emitted.circuit.reject_code == "E_QPU_CANONICAL_PROJECTION_UNAVAILABLE"
    assert emitted.circuit.gates == []
    assert emitted.circuit.allocation_started is False
    assert emitted.circuit.allocated_qubits == ()
    assert emitted.circuit.partial_program is None
