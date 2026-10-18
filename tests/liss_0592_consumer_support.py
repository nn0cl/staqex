"""R05 real entrypoints, with a recording SourcePort and trusted source corpus."""

from dataclasses import asdict

from compiler.staqex.access import find_module_info
from compiler.staqex.modules import _parse_file
from compiler.staqex.pipeline import compile_source


PROGRAMS = {
    "valid": "package t\npub fn main() -> Unit {\n State q = |0>\n Measure q\n}\n",
    "cardinality": "package t\npub fn main() -> Unit {\n Operator H = [X]\n}\n",
    "missing-brace": "package t\npub fn main() -> Unit {\n",
}
METADATA = {
    "valid": "module demo.app {\n exports visible;\n}\n",
    "missing-brace": "module demo.app {\n",
    "wrong-keyword": "wrong demo.app {}\n",
}
CASES = [(kind, name) for kind in ("pipeline", "module") for name in PROGRAMS]
CASES += [("access", name) for name in METADATA]


class RecordingSource:
    def __init__(self, path, source):
        self.path, self.source, self.calls = str(path), source, []

    def read_text(self, path):
        assert path == self.path
        self.calls.append(path)
        return self.source


def snapshot(kind, name, temporary_root):
    """No fake Parser/exception; filesystem metadata lives only in pytest temp."""
    temporary_root = temporary_root.resolve()
    source = METADATA[name] if kind == "access" else PROGRAMS[name]
    if kind == "pipeline":
        result = compile_source(source)
        return {"present": result.unit is not None, "local_ok": result.local_ok,
                "diagnostics": result.diagnostics}
    temporary_root.mkdir(parents=True, exist_ok=True)
    path = temporary_root / ("module-info.sqx" if kind == "access" else "sample.sqx")
    port = RecordingSource(path, source)
    if kind == "module":
        unit, diagnostics = _parse_file(path, source_port=port)
        result = {"present": unit is not None, "diagnostics": diagnostics}
    else:
        path.write_text(source)
        root, info, diagnostics = find_module_info(temporary_root, source_port=port)
        assert root == temporary_root
        result = {"present": info is not None,
                  "metadata": asdict(info) if info is not None else None,
                  "diagnostics": diagnostics}
    assert port.calls == [str(path)], "actual entrypoint must use the supplied port"
    return result
