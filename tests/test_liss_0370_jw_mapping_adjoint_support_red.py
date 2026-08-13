"""AT-TDD: LISS-0370 -- Jordan-Wigner mapping expands `adjoint(...)` of
a fermionic sub-expression (adjoint(create[i]) == annihilate[i]).

Design decision: docs/issues/LISS-0370-jw-mapping-adjoint-support.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source, run_source  # noqa: E402

_K = "1.0545718e-19"


def test_adjoint_inside_binder_matches_annihilate() -> None:
    def _prog(term: str) -> str:
        return f"""
        package t
        pub fn main() -> Unit {{
            QubitRegister<2> register = system()
            Operator H = Sigma (i In 0..1) {{ {_K} * (create[i] * {term}) }}
            State a = |+>
            State b = |0>
            State (a, b) = Evolve {{ (a, b) under H for 1.0.fs using Suzuki(order = 2, steps = 8) }}.run()
            State b = |0>
            Measure a
        }}
        """

    adj = run_source(_prog("adjoint(create[i])"), settings={"seed": 7})
    ann = run_source(_prog("annihilate[i]"), settings={"seed": 7})
    assert adj.status == "succeeded", adj.diagnostics
    assert ann.status == "succeeded", ann.diagnostics
    assert adj.measurements[0].marginal == ann.measurements[0].marginal


def test_adjoint_through_explicit_jordan_wigner_path() -> None:
    src = f"""
    package t
    pub fn main() -> Unit {{
        FermionOperator<Orbitals> H = {_K} * create[0] * adjoint(create[0])
        QubitOperator<Qubits> mapped = map(H, JordanWigner)
        State psi = |+>
        State psi = Evolve {{ psi under mapped for 1.0.fs using Suzuki(order = 2, steps = 8) }}.run()
        Measure psi
    }}
    """
    result = run_source(src, settings={"seed": 7})
    assert result.status == "succeeded", result.diagnostics


def test_non_adjoint_op_call_still_rejected() -> None:
    """Regression guard, at the unit level (bypassing the parser, since
    `commutator(...)` hits an unrelated, pre-existing gap in the
    Operator-DSL leading-atom heuristic that has nothing to do with
    this Issue): a genuinely unsupported OpCall name must still be
    rejected by `_expand`, not silently accepted by the new `adjoint`
    case."""
    from compiler.staqex.ast_nodes import OpCall, OpIndexed, OpLit, OpVar, Span
    from compiler.staqex.second_quantization import (
        SecondQuantizationMappingError,
        _expand,
    )

    span = Span(line=1, col=1)
    atom = OpIndexed(
        base=OpVar(name="create", span=span),
        index=OpLit(value=0, span=span),
        span=span,
    )
    call = OpCall(name="commutator", args=[atom, atom], span=span)
    try:
        _expand(call, {})
    except SecondQuantizationMappingError as exc:
        assert exc.code == "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED"
    else:
        raise AssertionError("expected SecondQuantizationMappingError")
