"""AT-TDD: LISS-0237 Kernel SourcePort (ADR 0172)."""

from __future__ import annotations

from canonical_execution import run_canonical

import subprocess
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.modules import load_module_graph  # noqa: E402
from compiler.staqex.pipeline import compile_path  # noqa: E402
from compiler.staqex.source_port import FilesystemSourceAdapter, SourcePort  # noqa: E402


def test_filesystem_adapter_implements_source_port() -> None:
    example = (
        _REPO
        / "examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx"
    )
    port: SourcePort = FilesystemSourceAdapter()
    text = port.read_text(str(example))
    # B01 may use default experiment profile (no package/main), explicit
    # profile marker, or packaged `main`.
    assert (
        "fn main" in text
        or "pub fn main" in text
        or "staqex-profile: experiment" in text
        or "Measure" in text
    )
    assert "Dirac" in text or "Measure" in text


def test_load_module_graph_reads_via_source_port() -> None:
    example = (
        _REPO
        / "examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx"
    )

    class CountingSource:
        def __init__(self) -> None:
            self.reads: list[str] = []
            self._inner = FilesystemSourceAdapter()

        def read_text(self, path: str) -> str:
            self.reads.append(str(Path(path).resolve()))
            return self._inner.read_text(path)

    port = CountingSource()
    graph = load_module_graph(example, source_port=port)
    assert not any(d.get("code") == "MODULE_NOT_FOUND_ERROR" for d in graph.diagnostics)
    assert example.resolve() in graph.units
    assert str(example.resolve()) in port.reads


def test_custom_source_port_overrides_disk_bytes() -> None:
    """Linker must parse port text, not silent disk bypass."""
    example = (
        _REPO
        / "examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx"
    )
    disk = example.read_text(encoding="utf-8")
    # Valid but different: keep package/main shape; change measured constant.
    overridden = disk.replace("42", "99", 1)
    assert overridden != disk

    class OverrideSource:
        def read_text(self, path: str) -> str:
            if Path(path).resolve() == example.resolve():
                return overridden
            return FilesystemSourceAdapter().read_text(path)

    compiled = compile_path(example, source_port=OverrideSource())
    assert compiled.ok and compiled.unit is not None
    # Disk still has 42; AST / source path must reflect override when evaluated.
    from compiler.staqex.runtime.evaluator import Evaluator
    import io

    result = run_canonical(compiled, Evaluator(seed=0), stdout=io.StringIO())
    assert result.measure is not None
    assert result.measure.output == "99"


def test_seed_zero_example_cli_output_stable() -> None:
    example = (
        _REPO
        / "examples/basics/B01_never_leave_the_state/never_leave_the_state.sqx"
    )
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "compiler.staqex",
            "run",
            str(example),
            "--seed",
            "0",
        ],
        cwd=_REPO,
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.stdout == "42\n"


if __name__ == "__main__":
    test_filesystem_adapter_implements_source_port()
    print("PASS adapter")
    test_load_module_graph_reads_via_source_port()
    print("PASS counting")
    test_custom_source_port_overrides_disk_bytes()
    print("PASS override")
    test_seed_zero_example_cli_output_stable()
    print("PASS seed pin")
    print("OK — LISS-0237")
