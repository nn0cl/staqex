"""Phase 1 Red contracts for WP-0140 / LISS-0523 X01."""

from __future__ import annotations

import importlib

import pytest


CITY_SENSOR_FIXTURE = (
    {
        "id": "city:demo",
        "revision": 1,
        "kind": "city-object",
        "source_id": "citygml:demo",
        "source_hash": "a" * 64,
        "profile": "geosensor-x01-v1",
        "geometry": {"type": "Point", "coordinates": [139.7, 35.6]},
        "crs": "EPSG:4326",
        "lod": "2.0",
    },
    {
        "id": "road:main",
        "revision": 1,
        "kind": "road",
        "source_id": "citygml:road-main",
        "source_hash": "b" * 64,
        "profile": "geosensor-x01-v1",
        "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 0]]},
        "crs": "EPSG:4326",
        "lod": "1.0",
    },
    {
        "id": "sensor:rain-01",
        "revision": 1,
        "kind": "sensor",
        "source_id": "sensorthings:sensor-01",
        "source_hash": "c" * 64,
        "profile": "geosensor-x01-v1",
        "procedure_id": "procedure:rain-gauge-v1",
        "property_id": "property:precipitation",
    },
    {
        "id": "observation:rain-01",
        "revision": 1,
        "kind": "observation",
        "source_id": "sosa:observation-01",
        "source_hash": "d" * 64,
        "profile": "geosensor-x01-v1",
        "foi_id": "road:main",
        "property_id": "property:precipitation",
        "procedure_id": "procedure:rain-gauge-v1",
        "phenomenon_time": "2026-09-16T00:00:00Z",
        "result_time": "2026-09-16T00:01:00Z",
        "ingest_time": "2026-09-16T00:02:00Z",
        "value": 0.0,
        "unit": "mm",
    },
)

RELATIONS = (
    ("city:demo", "contains", "road:main"),
    ("road:main", "toward", "city:demo"),
    ("road:main", "toward", "city:demo"),
    ("sensor:rain-01", "observes", "observation:rain-01"),
)


def _profile_module():
    """Load the X01 profile contract once its implementation exists."""

    try:
        return importlib.import_module("compiler.staqex.geospatial_metadata")
    except ModuleNotFoundError as error:
        raise AssertionError(
            "LISS-0523 requires compiler.staqex.geospatial_metadata: "
            "the X01 geospatial/sensor mapping contract is not implemented yet"
        ) from error


def _profile():
    module = _profile_module()
    return module.GeospatialMetadataProfile.from_records(
        CITY_SENSOR_FIXTURE,
        relations=RELATIONS,
    )


def test_x01_preserves_city_geometry_lod_graph_and_observation_roles() -> None:
    profile = _profile()

    assert profile.record("city:demo").geometry["type"] == "Point"
    assert profile.record("road:main").lod == "1.0"
    assert profile.relations.count(("road:main", "toward", "city:demo")) == 2
    observation = profile.record("observation:rain-01")
    assert observation.foi_id == "road:main"
    assert observation.property_id == "property:precipitation"
    assert observation.procedure_id == "procedure:rain-gauge-v1"
    assert observation.phenomenon_time != observation.result_time
    assert observation.result_time != observation.ingest_time
    assert observation.source_id == "sosa:observation-01"
    assert observation.source_hash == "d" * 64
    assert observation.mapping_evidence[0].source_hash == "d" * 64


def test_x01_retains_unknown_crs_and_uninterpreted_extensions_as_evidence() -> None:
    module = _profile_module()
    records = (
        {
            "id": "road:unknown-crs",
            "revision": 1,
            "kind": "road",
            "source_hash": "e" * 64,
            "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 0]]},
            "crs": None,
            "extensions": {"vendor:surface": "uninterpreted"},
        },
    )

    profile = module.GeospatialMetadataProfile.from_records(records)

    assert profile.record("road:unknown-crs").crs_state == "unknown"
    assert profile.raw_extension("road:unknown-crs", "vendor:surface").sha256
    assert profile.record("road:unknown-crs").mapping_evidence


def test_x01_quarantines_dangling_relation_endpoint() -> None:
    module = _profile_module()

    with pytest.raises(module.GeospatialProfileError):
        module.GeospatialMetadataProfile.from_records(
            CITY_SENSOR_FIXTURE,
            relations=(("road:main", "toward", "road:missing"),),
        )


def test_x01_quarantines_malformed_spatial_input() -> None:
    module = _profile_module()
    records = (
        CITY_SENSOR_FIXTURE[0],
        {**CITY_SENSOR_FIXTURE[0], "geometry": {"type": "Unknown"}},
    )

    with pytest.raises(module.GeospatialProfileError):
        module.GeospatialMetadataProfile.from_records(records)


def test_x01_geometry_does_not_infer_passability_or_tasking() -> None:
    profile = _profile()

    assert profile.domain_decision("road:main", "passable") is None
    assert profile.domain_decision("road:main", "routing") is None
    assert not hasattr(profile, "task_sensor")
    assert not hasattr(profile, "submit_task")


def test_x01_metadata_profile_cannot_be_used_as_execution_authority() -> None:
    profile = _profile()

    assert profile.is_executable is False
    assert not hasattr(profile, "execute")
    assert not hasattr(profile, "to_semantic_ir")
    assert not hasattr(profile, "project_to_qpu")


if __name__ == "__main__":
    tests = (
        test_x01_preserves_city_geometry_lod_graph_and_observation_roles,
        test_x01_retains_unknown_crs_and_uninterpreted_extensions_as_evidence,
        test_x01_quarantines_dangling_relation_endpoint,
        test_x01_quarantines_malformed_spatial_input,
        test_x01_geometry_does_not_infer_passability_or_tasking,
        test_x01_metadata_profile_cannot_be_used_as_execution_authority,
    )
    failures = 0
    for test in tests:
        try:
            test()
        except Exception as error:  # pragma: no cover - direct Red runner
            failures += 1
            print(f"FAIL {test.__name__}: {error}")
    print(f"LISS-0523 X01 Red: {len(tests) - failures} passed, {failures} failed")
    raise SystemExit(1 if failures else 0)
