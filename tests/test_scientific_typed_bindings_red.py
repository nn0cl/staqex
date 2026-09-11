"""Phase 1 Red tests for WP-0133 / LISS-0516 B01.

The binding module is intentionally not present until Phase 2.  These tests
define the approved Host-only contract without changing ScientificInput or
CoefficientTensor.
"""

from __future__ import annotations

import importlib

import pytest

from compiler.staqex.scientific_input import (
    CoefficientTensor,
    InputProvenance,
    ParameterBinding,
    ScientificInput,
)


SNAPSHOT = {
    "snapshot_id": "assay:snapshot-01",
    "revision": 4,
    "semantic_hash": "sha256:fixture-01",
}


def _binding_module():
    try:
        return importlib.import_module("compiler.staqex.scientific_bindings")
    except ModuleNotFoundError as error:
        pytest.fail(
            "LISS-0516 requires compiler.staqex.scientific_bindings: "
            "B01 BindingContract is not implemented yet"
        )
        raise AssertionError from error


def _contract(module, **overrides):
    values = {
        "source_symbol": "assay.activity",
        "snapshot_id": SNAPSHOT["snapshot_id"],
        "snapshot_revision": SNAPSHOT["revision"],
        "shape": (),
        "axis_map": (),
        "index_map": (),
        "unit": "rad",
        "dimension_signature": "Angle",
        "frame": None,
        "mapping_kind": "identity",
    }
    values.update(overrides)
    return module.BindingContract(**values)


def test_b01_scalar_binding_round_trips_source_and_snapshot_identity() -> None:
    module = _binding_module()
    source = ScientificInput(
        declared_parameters={"theta": "Angle"},
        bindings=(ParameterBinding("theta", 1.25, "rad"),),
        provenance=InputProvenance("theta = 1.25 rad", "input:theta-01"),
    )

    decoded = module.bind_input(
        source,
        _contract(module, source_symbol="theta"),
        snapshot=SNAPSHOT,
    )

    assert decoded.source_symbol == "theta"
    assert decoded.snapshot_id == SNAPSHOT["snapshot_id"]
    assert decoded.snapshot_revision == SNAPSHOT["revision"]
    assert decoded.semantic_hash == SNAPSHOT["semantic_hash"]
    assert decoded.mapping_evidence == ()


def test_b01_tensor_binding_preserves_named_axes_and_index_map() -> None:
    module = _binding_module()
    source = CoefficientTensor(
        name="velocity",
        shape=(2, 3),
        values=((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)),
        provenance=InputProvenance("v[i,j]", "input:velocity-01"),
    )
    contract = _contract(
        module,
        source_symbol="velocity",
        shape=(2, 3),
        axis_map=("latitude", "longitude"),
        index_map=(("latitude", (0, 1)), ("longitude", (0, 1, 2))),
        unit="m",
        dimension_signature="Length",
    )

    decoded = module.bind_input(source, contract, snapshot=SNAPSHOT)

    assert decoded.shape == (2, 3)
    assert decoded.axis_map == ("latitude", "longitude")
    assert decoded.index_map == contract.index_map


def test_b01_explicit_unit_mapping_requires_conversion_evidence() -> None:
    module = _binding_module()
    source = ParameterBinding("length", 10.0, "cm")
    contract = _contract(
        module,
        source_symbol="length",
        unit="m",
        dimension_signature="Length",
        mapping_kind="explicit_unit_conversion",
    )

    decoded = module.bind_input(
        source,
        contract,
        snapshot=SNAPSHOT,
        mapping_evidence={"from": "cm", "to": "m", "rule": "explicit"},
    )

    assert set(decoded.mapping_evidence) == {
        ("from", "cm"),
        ("rule", "explicit"),
        ("to", "m"),
    }


@pytest.mark.parametrize(
    "contract_overrides, snapshot",
    [
        ({}, {"snapshot_id": "assay:snapshot-01", "revision": 3}),
        ({"unit": "furlong", "dimension_signature": "Length"}, SNAPSHOT),
        ({"axis_map": ("longitude", "latitude"), "shape": (3, 2)}, SNAPSHOT),
    ],
)
def test_b01_rejects_stale_snapshot_unknown_unit_and_implicit_axis_change(
    contract_overrides: dict[str, object], snapshot: dict[str, object]
) -> None:
    module = _binding_module()
    source = CoefficientTensor(
        name="field",
        shape=(2, 3),
        values=((1.0, 2.0, 3.0), (4.0, 5.0, 6.0)),
        provenance=InputProvenance("field[i,j]", "input:field-01"),
    )

    with pytest.raises(module.BindingValidationError):
        module.bind_input(
            source,
            _contract(module, source_symbol="field", **contract_overrides),
            snapshot=snapshot,
        )


def test_b01_rejects_a_host_key_without_source_identity() -> None:
    module = _binding_module()

    with pytest.raises(module.BindingValidationError):
        module.bind_input(
            {"field": ((1.0, 2.0), (3.0, 4.0))},
            _contract(module, source_symbol=""),
            snapshot=SNAPSHOT,
        )
