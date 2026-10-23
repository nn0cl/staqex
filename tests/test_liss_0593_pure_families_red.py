"""F01–F06/F10: real behavior contracts and three independent ownership Reds."""

import ast
import base64
import copy
from dataclasses import fields, replace
import hashlib
import importlib
import inspect
import json
import pickle
import subprocess
import sys
from types import SimpleNamespace
from typing import Any

import pytest

from compiler.staqex.scientific_semantic import model
from tests import liss_0593_guard_support as guard

FUNCTIONS = tuple(guard.FUNCTIONS)
MODULES = tuple(guard.baseline()["exports"])
CORE_FIELDS = (
    "schema", "authority", "has_explicit_realize", "lowering_policy",
    "explicit_evolution", "realize_source_node_id", "finite_realization_record",
    "binder_lowering", "binder_source_node_ids", "binder_provenance", "projection_errors",
)


def reference(name):
    """Execute only the hash-pinned original function, never a proposed owner."""
    source = guard.definition(guard.evidence(guard.LEGACY), name)
    namespace = {"hashlib": hashlib, "json": json, "Any": Any,
                 "ScientificSemanticIR": model.ScientificSemanticIR,
                 "SemanticInspectionResult": model.SemanticInspectionResult,
                 "SemanticRejection": model.SemanticRejection}
    code = compile(b"from __future__ import annotations\n" + source,
                   "immutable-103fba43-" + name, "exec")
    exec(code, namespace)
    return namespace[name]


def entrypoints(name):
    return [getattr(importlib.import_module(module), name)
            for module in MODULES if hasattr(importlib.import_module(module), name)]


def populated():
    provenance = model.SemanticProvenance("理論.sqx", 2, 5, "n1")
    node = model.SemanticNode(
        "n1", "StateBind", ("c1", "c2"), "quantum", "State<T>", "2",
        "exact", "source", provenance, "coin", "mixture_source", ("c1",),
        "control", ((("branch", "left"),),), (("phase", 0.5),), "siblings", "tensor_product",
    )
    operation = model.CanonicalQpuOperation(
        "gate", (("source", "理論"),), "n1", "rx", (0,), 0.5, 2, 1, 1, 0, False,
    )
    record = model.FiniteRealizationRecord("r", "x", "y", "Suzuki", 2, 3, 0.1, (("source", "sqx"),))
    return model.ScientificSemanticIR(
        "ssc-v1", "scientific_semantic_ir", (node, replace(node, node_id="n2")),
        (model.SemanticRelation("flow", ("n1", "n2")), model.SemanticRelation("use", ("n2", "n1"))),
        has_explicit_realize=True,
        qpu_projection=model.CanonicalQpuProjection(2, (operation, replace(operation, opcode="ry"))),
        lowering_policy={"policy": "finite"}, explicit_evolution={"duration": 2},
        binder_lowering={"count": 3}, binder_source_node_ids=("b1", "b2"),
        binder_provenance=((("source", "binder"),),), projection_errors=("e1", "e2"),
        realize_source_node_id="r", finite_realization_record=record,
    )


def empty():
    return model.ScientificSemanticIR("ssc-v1", "scientific_semantic_ir", (), ())


def mixed_inspection():
    core = populated()
    node = core.nodes[0]
    nodes = (
        replace(node, node_id="n1", role_lane="quantum", type="State<Qubit>", dimensions="2"),
        replace(node, node_id="n2", role_lane="classical", type="Float", dimensions="3", exactness="unresolved"),
        replace(node, node_id="n3", role_lane="quantum", type="State<Int>", dimensions="5"),
    )
    return replace(core, nodes=nodes)


def different(value):
    if value is None:
        return "changed"
    if isinstance(value, bool):
        return not value
    if isinstance(value, str):
        return value + "!"
    if isinstance(value, (float, int)):
        return value + 1
    if isinstance(value, dict):
        return value | {"mutation": "changed"}
    if isinstance(value, tuple):
        return value + ("changed",)
    if isinstance(value, model.FiniteRealizationRecord):
        return replace(value, error_budget=0.2)
    raise AssertionError(type(value))


def assert_fingerprint_matches(core):
    expected = reference("semantic_fingerprint")(core)
    before = copy.deepcopy(core)
    for function in entrypoints("semantic_fingerprint"):
        assert function(core) == expected
        assert core == before
    return expected


@pytest.mark.parametrize("name", FUNCTIONS)
def test_f01_f05_sole_owner_contains_the_complete_original_algorithm(name):
    destination = guard.ROOT / guard.FUNCTIONS[name]
    raw = destination.read_bytes()
    assert guard.definition(raw, name) == guard.definition(guard.evidence(guard.LEGACY), name), "family still delegates instead of owning the algorithm"
    legacy = (guard.ROOT / guard.LEGACY).read_bytes()
    assert not any(isinstance(n, ast.FunctionDef) and n.name == name for n in ast.parse(legacy).body)
    owner = importlib.import_module("compiler.staqex.scientific_semantic." + destination.stem)
    retained = importlib.import_module("compiler.staqex.scientific_semantic.legacy")
    assert getattr(retained, name) is getattr(owner, name)
    assert guard.source_shape(guard.ROOT) == "post"


@pytest.mark.parametrize("core", [empty(), populated()], ids=["empty", "populated"])
def test_f02_complete_fingerprint_matches_original_without_mutation(core):
    assert len(assert_fingerprint_matches(core)) == 64


@pytest.mark.parametrize("field", CORE_FIELDS)
def test_f02_each_serialized_core_field_changes_the_original_digest(field):
    core = populated()
    mutated = replace(core, **{field: different(getattr(core, field))})
    assert assert_fingerprint_matches(mutated) != assert_fingerprint_matches(core)


@pytest.mark.parametrize("field", [f.name for f in fields(model.SemanticNode)])
def test_f02_each_serialized_node_field_is_preserved(field):
    core = populated()
    changed = replace(core.nodes[0], **{field: different(getattr(core.nodes[0], field))})
    assert assert_fingerprint_matches(replace(core, nodes=(changed, *core.nodes[1:]))) != assert_fingerprint_matches(core)


@pytest.mark.parametrize("field", [f.name for f in fields(model.SemanticRelation)])
def test_f02_each_serialized_relation_field_is_preserved(field):
    core = populated()
    relation = core.relations[0]
    changed = replace(relation, **{field: different(getattr(relation, field))})
    assert [f.name for f in fields(relation) if getattr(changed, f.name) != getattr(relation, f.name)] == [field]
    mutated = replace(core, relations=(changed, *core.relations[1:]))
    assert assert_fingerprint_matches(mutated) != assert_fingerprint_matches(core)


@pytest.mark.parametrize("field", [f.name for f in fields(model.CanonicalQpuOperation)])
def test_f02_each_serialized_operation_field_is_preserved(field):
    core = populated()
    projection = core.qpu_projection
    changed = replace(projection.operations[0], **{field: different(getattr(projection.operations[0], field))})
    mutated = replace(core, qpu_projection=replace(projection, operations=(changed, *projection.operations[1:])))
    assert assert_fingerprint_matches(mutated) != assert_fingerprint_matches(core)


@pytest.mark.parametrize("field", [f.name for f in fields(model.FiniteRealizationRecord)])
def test_f02_default_str_preserves_each_realization_record_field(field):
    core = populated()
    record = replace(core.finite_realization_record, **{field: different(getattr(core.finite_realization_record, field))})
    assert assert_fingerprint_matches(replace(core, finite_realization_record=record)) != assert_fingerprint_matches(core)


@pytest.mark.parametrize("part", ["nodes", "relations", "operations", "logical_qubits", "projection_error", "projection_none"])
def test_f02_sequence_order_and_projection_boundary(part):
    core = populated()
    if part in {"nodes", "relations"}:
        mutated = replace(core, **{part: tuple(reversed(getattr(core, part)))})
    elif part == "projection_none":
        mutated = replace(core, qpu_projection=None)
    else:
        projection = core.qpu_projection
        value = tuple(reversed(projection.operations)) if part == "operations" else 3 if part == "logical_qubits" else "rejected"
        mutated = replace(core, qpu_projection=replace(projection, **{part: value}))
    assert assert_fingerprint_matches(mutated) != assert_fingerprint_matches(core)


def test_f02_json_parameters_default_and_hash_input_are_unchanged(monkeypatch):
    class Opaque:
        def __str__(self):
            return "非JSON値"

    core = replace(populated(), lowering_policy={"custom": Opaque()})
    dumps, digest = json.dumps, hashlib.sha256
    calls, inputs = [], []

    def recording_json(value, **kwargs):
        calls.append(kwargs)
        return dumps(value, **kwargs)

    def recording_hash(value):
        inputs.append(value)
        return digest(value)

    monkeypatch.setattr(json, "dumps", recording_json)
    monkeypatch.setattr(hashlib, "sha256", recording_hash)
    # Construct the trusted function before recording, excluding evidence hashes.
    baseline_function = reference("semantic_fingerprint")
    calls.clear()
    inputs.clear()
    expected = baseline_function(core)
    for function in entrypoints("semantic_fingerprint"):
        assert function(core) == expected
    assert all(call == {"sort_keys": True, "separators": (",", ":"), "default": str} for call in calls)
    assert len(calls) == len(inputs) == 1 + len(entrypoints("semantic_fingerprint"))
    assert all(value == inputs[0] and value.decode("utf-8").encode("utf-8") == value for value in inputs)


@pytest.mark.parametrize(
    "core",
    [empty(), populated(),
     replace(populated(), nodes=tuple(replace(n, exactness="unresolved") for n in populated().nodes)),
     mixed_inspection()],
    ids=["empty", "duplicate-lanes", "unresolved", "mixed-lanes-exactness-dimensions"],
)
def test_f03_inspection_order_exactness_and_original_object_identity(core):
    expected = reference("build_inspection")(core)
    for function in entrypoints("build_inspection"):
        actual = function(core)
        assert actual == expected and type(actual) is model.SemanticInspectionResult
        assert actual.structural_tree is core.nodes
        assert actual.role_lanes == tuple(dict.fromkeys(n.role_lane for n in core.nodes))
        assert actual.type_dimensions == tuple((n.type, n.dimensions) for n in core.nodes)
        assert actual.exactness == ("exact" if all(n.exactness == "exact" for n in core.nodes) else "unresolved")


@pytest.mark.parametrize("diagnostics", [[], [{}], [{"code": None}], [{"code": 42}], [{"code": "first"}, {"code": "second"}], [{"message": "ignored"}, {"code": "later"}]])
@pytest.mark.parametrize("core", [empty(), populated()], ids=["empty", "populated"])
def test_f03_rejection_uses_original_first_diagnostic_and_order(core, diagnostics):
    before = copy.deepcopy(diagnostics)
    expected = reference("build_rejection")(core, diagnostics)
    for function in entrypoints("build_rejection"):
        actual = function(core, diagnostics)
        assert actual == expected
        if diagnostics:
            assert type(actual) is model.SemanticRejection
            assert actual.code == str(diagnostics[0].get("code", "SSC_UNRESOLVED_MEANING"))
            assert actual.spans == tuple((n.provenance[1], n.provenance[2]) for n in core.nodes)
        else:
            assert actual is None
        assert diagnostics == before


def outcome(function, *args):
    try:
        return ("result", function(*args))
    except Exception as error:
        return ("error", type(error), error.args)


@pytest.mark.parametrize("name,args", [
    ("semantic_fingerprint", (None,)),
    ("semantic_fingerprint", (SimpleNamespace(schema="s"),)),
    ("build_inspection", (None,)),
    ("build_inspection", (replace(empty(), nodes=(object(),)),)),
    ("build_rejection", (None, [])),
    ("build_rejection", (populated(), [None])),
    ("build_rejection", (populated(), [42])),
    ("build_rejection", (replace(populated(), nodes=(replace(populated().nodes[0], provenance=()),)), [{}])),
])
def test_f02_f03_malformed_inputs_keep_original_failure_boundary(name, args):
    expected = outcome(reference(name), *args)
    for function in entrypoints(name):
        assert outcome(function, *args) == expected


def test_f02_circular_json_keeps_original_error():
    recursive = {}
    recursive["self"] = recursive
    core = replace(populated(), lowering_policy=recursive)
    expected = outcome(reference("semantic_fingerprint"), core)
    assert expected[0:2] == ("error", ValueError)
    for function in entrypoints("semantic_fingerprint"):
        assert outcome(function, core) == expected


@pytest.mark.parametrize("module_name", MODULES)
def test_f04_signatures_wildcards_and_shared_model_classes(module_name):
    module = importlib.import_module(module_name)
    namespace = {}
    exec("from " + module_name + " import *", namespace)
    assert sorted(n for n in namespace if not n.startswith("_")) == guard.baseline()["exports"][module_name]
    for name, signature in guard.baseline()["signatures"][module_name].items():
        assert str(inspect.signature(getattr(module, name))) == signature
    for name, value in vars(model).items():
        if isinstance(value, type) and value.__module__ == model.__name__ and hasattr(module, name):
            assert getattr(module, name) is value


@pytest.mark.parametrize("name", FUNCTIONS)
def test_f04_old_legacy_callable_pickle_resolves_current_binding(name):
    loaded = pickle.loads(base64.b64decode(guard.baseline()["legacy_callable_pickles"][name]))
    assert loaded is getattr(importlib.import_module("compiler.staqex.scientific_semantic.legacy"), name)


@pytest.mark.parametrize("first", MODULES)
def test_f04_f05_cold_actual_consumer_imports(first):
    consumers = [first, *MODULES, "compiler.staqex.pipeline", "compiler.staqex.qpu_ir",
                 "compiler.staqex.physics_ir_lower", "compiler.staqex.symbolic_ir",
                 "compiler.staqex.backend.qasm.emitter", "compiler.staqex.realization_artifact"]
    result = subprocess.run([sys.executable, "-c", "import importlib; [importlib.import_module(n) for n in " + repr(consumers) + "]"],
                            cwd=guard.ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_f06_other_production_and_original_non_target_bodies_are_frozen():
    assert set(guard.baseline()["production_sha256"]) == set(subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "compiler"], cwd=guard.ROOT, text=True).splitlines())
    for path, digest in guard.baseline()["production_sha256"].items():
        assert guard.sha(guard.readonly_bytes(guard.ROOT, path)) == digest, path


def test_f10_no_production_test_guard_or_historical_fixture_edit_during_red():
    # Applies to the authored Red checkpoint. Future production shape is checked
    # by F06; old carrier changes must be exactly the already-reviewed proposal.
    for path in guard.CARRIERS:
        data = (guard.ROOT / path).read_bytes()
        assert guard.historical_carrier_bytes(guard.ROOT, path, data) == guard.evidence(path)
