"""AT-TDD: LISS-0236 Kernel MeasureSinkPort (ADR 0171)."""

from __future__ import annotations

import io
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.measure_sink_port import (  # noqa: E402
    FileMeasureSinkAdapter,
    MeasureSinkPort,
    TextIOMeasureSinkAdapter,
    resolve_measure_sink,
)
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_textio_adapter_implements_measure_sink_port() -> None:
    buf = io.StringIO()
    port: MeasureSinkPort = TextIOMeasureSinkAdapter(buf)
    port.write("hello\n")
    assert buf.getvalue() == "hello\n"


def test_file_adapter_overwrites_path() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "out.txt"
        port: MeasureSinkPort = FileMeasureSinkAdapter(path)
        port.write("a\n")
        port.write("b\n")
        assert path.read_text(encoding="utf-8") == "b\n"


def test_resolve_stdout_alias_uses_textio() -> None:
    buf = io.StringIO()
    port = resolve_measure_sink("stdout", stdout=buf)
    assert port is not None
    port.write("x\n")
    assert buf.getvalue() == "x\n"


def test_custom_measure_sink_port_receives_measure_text() -> None:
    class CaptureSink:
        def __init__(self) -> None:
            self.chunks: list[str] = []

        def write(self, text: str) -> None:
            self.chunks.append(text)

    src = """
    package t
    pub fn main() -> Unit {
        State a = Coin()
        Measure a
    }
    """
    compiled = compile_source(src)
    assert compiled.ok and compiled.unit is not None
    sink = CaptureSink()
    # seed picks a deterministic atom; port must still receive the formatted line.
    ev = Evaluator(seed=0, measure_sink=sink)
    result = ev.run_unit(compiled.unit, stdout=io.StringIO())
    assert result.measure is not None
    assert result.measure.output
    assert sink.chunks == [result.measure.output + "\n"]


def test_seed_zero_example_cli_output_stable() -> None:
    """Published example --seed 0 output must remain bit-identical."""
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
    test_textio_adapter_implements_measure_sink_port()
    print("PASS textio")
    test_file_adapter_overwrites_path()
    print("PASS file")
    test_resolve_stdout_alias_uses_textio()
    print("PASS resolve")
    test_custom_measure_sink_port_receives_measure_text()
    print("PASS custom")
    test_seed_zero_example_cli_output_stable()
    print("PASS seed pin")
    print("OK — LISS-0236")
