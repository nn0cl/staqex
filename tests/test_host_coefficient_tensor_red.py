"""AT-TDD: LISS-0150 Host CoefficientTensor inject (ADR 0119)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.finite_binder import (  # noqa: E402
    lower_finite_binder_operators,
    merge_host_coefficient_arrays,
)
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.scientific_input import (  # noqa: E402
    CoefficientTensor,
    InputProvenance,
    ScientificInputValidationError,
)


def _prov() -> InputProvenance:
    return InputProvenance(source_formula="h_matrix", input_id="test-h")


def test_coefficient_tensor_rejects_nonfinite() -> None:
    try:
        CoefficientTensor(
            name="h",
            shape=(2,),
            values=[1.0, float("nan")],
            provenance=_prov(),
        )
    except ScientificInputValidationError as error:
        assert error.code == "HOST_COEFFICIENT_VALUE_ERROR"
    else:
        raise AssertionError("expected validation error")


def test_host_placeholder_lowers_with_overlay() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Float[2][2] h = host("h")
        Operator H = Sigma (p In 0..1, q In 0..1) {
            h[p][q] * Z[p] * Z[q]
        }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(source)
    codes = {d.get("code", "") for d in compiled.diagnostics}
    assert "PARSE_ERROR" not in codes, codes
    assert "TYPE_MISMATCH" not in codes, codes
    assert compiled.unit is not None
    tensor = CoefficientTensor(
        name="h",
        shape=(2, 2),
        values=[[1.0, 0.0], [0.0, 0.5]],
        provenance=_prov(),
    )
    arrays, diags = merge_host_coefficient_arrays(compiled.unit, {"h": tensor})
    assert not diags, diags
    assert "h" in arrays
    lowered, lower_diags = lower_finite_binder_operators(
        compiled.unit, host_arrays=arrays
    )
    assert not lower_diags, lower_diags
    assert "H" in lowered


def test_missing_host_coefficient_is_diagnosed() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        QubitRegister<2> register = system()
        Float[2] J = host("J")
        Operator H = Sigma (i In 0..0) { J[i] * Z[i] }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None
    _, diags = merge_host_coefficient_arrays(compiled.unit, {})
    assert any(d.get("code") == "HOST_COEFFICIENT_MISSING" for d in diags)


def test_literal_and_host_conflict() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        Float[2] J = [1.0, 0.5]
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(source)
    assert compiled.unit is not None
    tensor = CoefficientTensor(
        name="J", shape=(2,), values=[1.0, 0.5], provenance=_prov()
    )
    _, diags = merge_host_coefficient_arrays(compiled.unit, {"J": tensor})
    assert any(d.get("code") == "HOST_COEFFICIENT_CONFLICT" for d in diags)


if __name__ == "__main__":
    test_coefficient_tensor_rejects_nonfinite()
    print("PASS test_coefficient_tensor_rejects_nonfinite")
    test_host_placeholder_lowers_with_overlay()
    print("PASS test_host_placeholder_lowers_with_overlay")
    test_missing_host_coefficient_is_diagnosed()
    print("PASS test_missing_host_coefficient_is_diagnosed")
    test_literal_and_host_conflict()
    print("PASS test_literal_and_host_conflict")
