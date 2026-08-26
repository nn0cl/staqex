"""AT-TDD: LISS-0220 — the QFT family infers as Operator, not State.

The declared Type-First head hides this defect in ordinary programs, so these
assertions read `TypeChecker.typed` directly. That map is what HIR analyses
consult (see ADR 0167), which is where the mis-inference actually bit.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import StateBind  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _binds(node: object, out: list[StateBind]) -> None:
    if isinstance(node, StateBind):
        out.append(node)
    for value in getattr(node, "__dict__", {}).values():
        if isinstance(value, list):
            for item in value:
                _binds(item, out)
        elif hasattr(value, "__dict__"):
            _binds(value, out)


def _inferred_kind(source: str, bind_name: str) -> str | None:
    compiled = compile_source(source)
    assert compiled.checker is not None, compiled.diagnostics
    found: list[StateBind] = []
    _binds(compiled.unit, found)
    for stmt in found:
        if stmt.names and stmt.names[0] == bind_name:
            ty = compiled.checker.typed.get(id(stmt.expr))
            return ty.kind if ty is not None else None
    raise AssertionError(f"no bind named {bind_name!r}")


def _program(body: str) -> str:
    return (
        "package t\n"
        "pub fn main() -> Unit {\n"
        f"    {body}\n"
        "    State<Int> observed = Coin()\n"
        "    Measure observed\n"
        "}\n"
    )


def test_qft_infers_as_operator() -> None:
    kind = _inferred_kind(
        _program("QubitRegister<3> reg = system()\n    Operator F = qft(reg)"),
        "F",
    )
    assert kind == "Operator", f"qft(reg) inferred {kind}, expected Operator"


def test_iqft_infers_as_operator() -> None:
    kind = _inferred_kind(
        _program("QubitRegister<3> reg = system()\n    Operator F = iqft(reg)"),
        "F",
    )
    assert kind == "Operator", f"iqft(reg) inferred {kind}, expected Operator"


def test_cqft_infers_as_operator() -> None:
    kind = _inferred_kind(
        _program(
            "QubitRegister<1> ctrl = system()\n"
            "    QubitRegister<2> reg = system()\n"
            "    Operator F = cqft(ctrl, reg)"
        ),
        "F",
    )
    assert kind == "Operator", f"cqft inferred {kind}, expected Operator"


def test_ciqft_infers_as_operator() -> None:
    kind = _inferred_kind(
        _program(
            "QubitRegister<1> ctrl = system()\n"
            "    QubitRegister<2> reg = system()\n"
            "    Operator F = ciqft(ctrl, reg)"
        ),
        "F",
    )
    assert kind == "Operator", f"ciqft inferred {kind}, expected Operator"


def test_qft_operator_bind_carries_no_linear_obligation() -> None:
    """ADR 0167: an Operator is not a linear quantum carrier.

    Regression guard for the interaction that surfaced this Issue — a QFT bind
    left undischarged must not be reported as discarded quantum state.
    """
    compiled = compile_source(
        _program("QubitRegister<3> reg = system()\n    Operator F = qft(reg)")
    )
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "LINEAR_IMPLICIT_DISCARD" not in codes, compiled.diagnostics


if __name__ == "__main__":
    _failed = 0
    for _name, _fn in sorted(globals().items()):
        if _name.startswith("test_") and callable(_fn):
            try:
                _fn()
            except AssertionError as _error:
                _failed += 1
                print(f"FAIL: {_name}: {_error}")
            else:
                print(f"PASS {_name}")
    raise SystemExit(1 if _failed else 0)
