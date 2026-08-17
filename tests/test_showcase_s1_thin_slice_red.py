"""AT-TDD: LISS-0134 Showcase S1 vertical thin slice (quantum-matter discovery)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_path, compile_source, run_path  # noqa: E402

_SHOWCASE_ROOT = _REPO / "examples/showcase/quantum_matter_discovery"
_ENTRY = _SHOWCASE_ROOT / "main_quantum_matter_discovery.sqx"


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def test_s1_entry_exists() -> None:
    assert _ENTRY.is_file(), f"missing S1 entrypoint {_ENTRY}"


def test_s1_module_tree_has_domain_and_physics() -> None:
    domain = list((_SHOWCASE_ROOT / "domain").glob("*.sqx"))
    physics = list((_SHOWCASE_ROOT / "physics").glob("*.sqx"))
    assert domain, "S1 requires domain/*.sqx bounded-context modules"
    assert physics, "S1 requires physics/*.sqx Operator modules"


def test_s1_spine_compiles_and_runs() -> None:
    compiled = compile_path(str(_ENTRY))
    hard = _hard(compiled.diagnostics)
    assert compiled.ok or not hard, hard
    result = run_path(
        str(_ENTRY),
        settings={"target": "local", "seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", _hard(result.diagnostics)


def test_s1_source_exercises_required_surfaces() -> None:
    """Coverage subset from S0 §4 (string presence in the spine tree)."""
    texts = []
    for path in _SHOWCASE_ROOT.rglob("*.sqx"):
        texts.append(path.read_text(encoding="utf-8"))
    blob = "\n".join(texts)
    assert "Mix (" in blob
    assert "expect(" in blob
    assert "Inspect(" in blob
    assert "Measure " in blob
    assert "Evolve()" in blob
    assert "Float " in blob
    assert "Operator " in blob
    assert "struct " in blob or "namespace " in blob
    assert "if " not in blob.replace("//", "")


def test_s1_classical_if_still_fail_closed() -> None:
    """Diagnostics honesty fixture (S0 ports/diagnostics required row)."""
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State x = |0>
            if (true) { Measure x }
        }
        """
    )
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "PARSE_ERROR" in codes or any(
        "if" in (d.get("message") or "").lower() for d in compiled.diagnostics
    )


if __name__ == "__main__":
    test_s1_classical_if_still_fail_closed()
    test_s1_entry_exists()
    test_s1_module_tree_has_domain_and_physics()
    test_s1_spine_compiles_and_runs()
    test_s1_source_exercises_required_surfaces()
    print("OK — showcase S1")
