"""AT-TDD Phase 1 Red -> Green: `Sigma (x In F) { |x><x| }` -- Sigma over
a general `Set` domain, plus the bound-variable projector term `|x><x|`
(Pauli-Z decomposition).

Target: docs/issues/LISS-0430-sigma-over-set-projector.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.hamiltonian import compile_hamiltonian  # noqa: E402


def _p_f_matrix(src: str, n_qubits: int):
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    ev = Evaluator(seed=0)
    ev.run_unit(compiled.unit)
    op_ast = ev.operators.get("P_F")
    assert op_ast is not None
    return compile_hamiltonian(op_ast, env={}, n_qubits=n_qubits)


def test_ket_bra_lexes_as_projector_not_comparison() -> None:
    """LISS-0430 found this was a real, previously-dead lexer gap: `|x><x|`
    (ADR 0169 Slice D) could never actually be reached because
    `_can_start_primary` blocked `<` from starting a bra literal right
    after a closed ket."""
    from compiler.staqex.lexer import Lexer
    from compiler.staqex.tokens import TokenKind

    tokens, diags = Lexer("|x><x|").tokenize()
    assert diags == []
    kinds = [t.kind for t in tokens if t.kind != TokenKind.EOF]
    assert kinds == [TokenKind.KET, TokenKind.BRA]


def test_projector_matrix_matches_hand_computed_diagonal_n2() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Set F = { x In {0,1}^n : x[0] == 1 }
        Operator P_F = Sigma (x In F) { |x><x| }
        State a = |0>
        Measure a
    }
    """
    mat = _p_f_matrix(src, 2)
    # F = {(1,0), (1,1)} -> big-endian indices 2, 3.
    diag = [round(mat[i][i].real, 6) for i in range(4)]
    assert diag == [0.0, 0.0, 1.0, 1.0]
    off_diag = [
        mat[i][j] for i in range(4) for j in range(4) if i != j
    ]
    assert all(abs(v) < 1e-9 for v in off_diag)


def test_projector_matrix_matches_target_shape_n3() -> None:
    """The exact confirmed S02 `F` (all three conditions), n=3 -- cross-
    checked against the same hand-enumerated ground truth LISS-0429's own
    test used (F = {(1,0,1), (1,1,0)} -> indices 5, 6)."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 3
        Set F = {
            x In {0,1}^n :
                Sigma (i In 0..n-1) { x[i] } == 2,
                ForAll (i In 0..n-1, j In 0..n-1) where i < j {
                    (x[i] * x[j] == 1) Implies (i + j <= 2)
                },
                Min (i In 0..n-1, j In 0..n-1) where i < j, x[i] * x[j] == 1 { i + j } >= 1
        }
        Operator P_F = Sigma (x In F) { |x><x| }
        State a = |0>
        Measure a
    }
    """
    mat = _p_f_matrix(src, 3)
    diag = [round(mat[i][i].real, 6) for i in range(8)]
    assert diag == [0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0]
    off_diag = [
        mat[i][j] for i in range(8) for j in range(8) if i != j
    ]
    assert all(abs(v) < 1e-9 for v in off_diag)


def test_empty_set_gives_the_zero_operator() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Set F = { x In {0,1}^n : x[0] == 1, x[0] == 0 }
        Operator P_F = Sigma (x In F) { |x><x| }
        State a = |0>
        Measure a
    }
    """
    mat = _p_f_matrix(src, 2)
    assert all(abs(v) < 1e-9 for row in mat for v in row)


def test_sigma_over_set_body_must_be_bound_variable_projector() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Set F = { x In {0,1}^n : x[0] == 1 }
        Operator P_F = Sigma (x In F) { Z[0] }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    try:
        Evaluator(seed=0).run_unit(compiled.unit)
        raise AssertionError("expected KernelError for non-projector body")
    except Exception as e:  # noqa: BLE001
        assert "requires the body to be exactly" in str(e)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0430 Slice B Phase 2 Green")
