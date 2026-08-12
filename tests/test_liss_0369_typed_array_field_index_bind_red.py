"""AT-TDD: LISS-0369 -- `Float[M...] row = expr[i]` RHS recognizes a
struct/class-field array before the index, not just a bare variable.

Design decision: docs/issues/LISS-0369-typed-array-field-index-bind.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402


def test_class_field_array_index_bind_reaches_the_correct_diagnostic() -> None:
    """LISS-0369 fixes the parser-level misrouting only: `m.h[1]` must
    now reach the Operator-DSL grammar (no more PARSE_ERROR) and fail
    with the accurate ADR 0118 diagnostic instead -- struct/class
    field-array shape tracking is a separate, larger future Issue, not
    yet implemented, so this does not assert full compile success."""
    src = """
    package t
    namespace D {
      pub class Mat {
        pub val h: Float[2][2]
        fn init(h: Float[2][2]) { this.h = h }
      }
    }
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        D.Mat m = D.Mat([[1.0, 0.0], [0.0, 0.5]])
        Float[2] row = m.h[1]
        Operator H = sum (q in Index<0..1>) {
            row[q] * Z[q]
        }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "PARSE_ERROR" not in codes, compiled.diagnostics
    assert "TYPE_MISMATCH" in codes, compiled.diagnostics
    messages = " ".join(d.get("message", "") for d in compiled.diagnostics)
    assert "Float[…] tensor root" in messages or "Float[" in messages, (
        compiled.diagnostics
    )


def test_bare_variable_array_index_bind_still_parses() -> None:
    """Regression guard: the pre-existing ADR 0118 / LISS-0149 form."""
    src = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Float[2][2] h = [
            [1.0, 0.0],
            [0.0, 0.5],
        ]
        Float[2] row = h[1]
        Operator H = sum (q in Index<0..1>) {
            row[q] * Z[q]
        }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert compiled.ok, compiled.diagnostics
