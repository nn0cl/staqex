"""AT-TDD Phase 1 Red: LISS-0032 typed second-quantized operators."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.symbolic_ir import build_symbolic_ir  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_typed_fermion_operator_family_is_distinct() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            FermionOperator<Orbitals> H = create[0] * annihilate[0]
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_fermion_and_boson_families_cannot_be_mixed() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            FermionOperator<Orbitals> fermion = create[0]
            BosonOperator<Modes> boson = create[0]
            FermionOperator<Orbitals> invalid = fermion + boson
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "SECOND_QUANTIZATION_TYPE_ERROR" in codes


def test_mapping_to_qubit_operator_is_explicit() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            FermionOperator<Orbitals> H = create[0] * annihilate[0]
            QubitOperator<Qubits> mapped = map(H, JordanWigner)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics


def test_second_quantized_operations_do_not_measure() -> None:
    codes = _codes(
        """
        package t
        pub fn main() -> Unit {
            FermionOperator<Orbitals> invalid = create(Measure(|0>))
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "EARLY_COLLAPSE_ERROR" in codes


def test_fermion_canonical_order_records_exchange_sign() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            FermionOperator<Orbitals> H = create[1] * create[0]
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.unit is not None
    metadata = build_symbolic_ir(compiled.unit)["operators"]["H"]["second_quantized"]
    assert metadata["statistics"] == "fermionic"
    assert metadata["canonical_order"][0]["index"] == 0
    assert metadata["exchange_sign"] == -1


def test_boson_order_does_not_introduce_fermion_sign() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            BosonOperator<Modes> H = create[1] * create[0]
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.unit is not None
    metadata = build_symbolic_ir(compiled.unit)["operators"]["H"]["second_quantized"]
    assert metadata["exchange_sign"] == 1


def test_mapping_name_is_recorded_in_symbolic_ir() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            FermionOperator<Orbitals> H = create[0] * annihilate[0]
            QubitOperator<Qubits> mapped = map(H, JordanWigner)
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.unit is not None
    assert build_symbolic_ir(compiled.unit)["resolved"]["mappings"] == [
        {"operator": "mapped", "mapping": "JordanWigner", "qubit_count": 1}
    ]


if __name__ == "__main__":
    for test in (
        test_typed_fermion_operator_family_is_distinct,
        test_fermion_and_boson_families_cannot_be_mixed,
        test_mapping_to_qubit_operator_is_explicit,
        test_second_quantized_operations_do_not_measure,
        test_fermion_canonical_order_records_exchange_sign,
        test_boson_order_does_not_introduce_fermion_sign,
        test_mapping_name_is_recorded_in_symbolic_ir,
    ):
        test()
    print("OK — second-quantized operator tests")
