"""H01–H07: characterize the live private Host input boundary without a new owner."""

from types import SimpleNamespace
import subprocess
import sys

import pytest

from compiler.staqex import finite_binder, scientific_input
from compiler.staqex.pipeline import compile_source
from compiler.staqex.runtime.evaluation import execution
from compiler.staqex.runtime.evaluator import Evaluator, KernelDiagnosticError


class RecordingPort:
    def __init__(self, values):
        self.values = values
        self.reads = []

    def get(self, name):
        self.reads.append(name)
        return self.values.get(name)


def unit_for(declarations=""):
    compiled = compile_source(
        f"package t\npub fn main() -> Unit {{ {declarations} State q = |0> Measure q }}"
    )
    assert compiled.unit is not None, compiled.diagnostics
    assert not any(d.get("code") == "PARSE_ERROR" for d in compiled.diagnostics)
    return compiled.unit


def resolve(declarations, values):
    port = RecordingPort(values)
    evaluator = Evaluator(host_input=port)
    return evaluator._resolve_host_coefficient_arrays(unit_for(declarations)), port


@pytest.mark.parametrize("declarations", ["", "Float[2] a = [1.0, 2.0]"])
def test_h01_no_placeholder_never_reads_or_merges(declarations, monkeypatch):
    def forbidden(*args):
        pytest.fail("no-placeholder path must not merge")
    monkeypatch.setattr(finite_binder, "merge_host_coefficient_arrays", forbidden)
    arrays, port = resolve(declarations, {"unused": [99]})
    assert arrays == {} and port.reads == []


def test_h01_no_main_never_reads():
    port = RecordingPort({"a": [1]})
    assert Evaluator(host_input=port)._resolve_host_coefficient_arrays(SimpleNamespace(main=None)) == {}
    assert port.reads == []


def test_h02_order_deduplication_and_extra_inputs():
    arrays, port = resolve(
        'Float[1] a = host("z") Float[1] b = host("a") Float[1] c = host("z")',
        {"z": [3], "a": [7], "unused": object()},
    )
    assert port.reads == ["z", "a"]
    assert arrays == {"a": [3.0], "b": [7.0], "c": [3.0]}


def test_h02_missing_repeated_key_is_not_cached():
    port = RecordingPort({})
    with pytest.raises(KernelDiagnosticError, match="missing Host coefficient `x`") as caught:
        Evaluator(host_input=port)._resolve_host_coefficient_arrays(
            unit_for('Float[1] a = host("x") Float[1] b = host("x")')
        )
    assert port.reads == ["x", "x"]
    assert caught.value.code == "HOST_COEFFICIENT_MISSING"
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("dtype,values,expected", [
    ("Float", [[1, 2], [3, 4]], [[1.0, 2.0], [3.0, 4.0]]),
    ("Bool", [[True, False], [False, True]], [[True, False], [False, True]]),
])
def test_h03_nested_dtype_and_fresh_live_port(dtype, values, expected):
    unit = unit_for(f'{dtype}[2][2] a = host("x")')
    first = RecordingPort({"x": values})
    evaluator = Evaluator(host_input=first)
    result = evaluator._resolve_host_coefficient_arrays(unit)
    assert result == {"a": expected}
    assert type(result["a"][0][0]) is (float if dtype == "Float" else bool)
    second = RecordingPort({"x": values})
    evaluator.host_input = second
    result["a"][0][0] = "mutated result"
    assert evaluator._resolve_host_coefficient_arrays(unit) == {"a": expected}
    assert first.reads == second.reads == ["x"]


@pytest.mark.parametrize("dtype,shape,raw,code", [
    ("Float", "[2]", [1], "HOST_COEFFICIENT_SHAPE_ERROR"),
    ("Float", "[1]", ["bad"], "HOST_COEFFICIENT_VALUE_ERROR"),
    ("Float", "[1]", [True], "HOST_COEFFICIENT_VALUE_ERROR"),
    ("Bool", "[1]", [1], "HOST_COEFFICIENT_VALUE_ERROR"),
    ("Float", "[1]", [float("nan")], "HOST_COEFFICIENT_VALUE_ERROR"),
    ("Float", "[1]", [float("inf")], "HOST_COEFFICIENT_VALUE_ERROR"),
    ("Float", "[1]", [float("-inf")], "HOST_COEFFICIENT_VALUE_ERROR"),
    ("Float", "[2][2]", [[1, 2], [3]], "HOST_COEFFICIENT_SHAPE_ERROR"),
    ("Float", "[1000001]", [], "HOST_COEFFICIENT_RESOURCE_ERROR"),
])
def test_h04_error_code_message_class_and_cause(dtype, shape, raw, code):
    with pytest.raises(KernelDiagnosticError) as caught:
        resolve(f'{dtype}{shape} a = host("x")', {"x": raw})
    error = caught.value
    assert error.code == code and isinstance(error, ValueError)
    assert type(error.__cause__) is scientific_input.ScientificInputValidationError
    assert str(error) == str(error.__cause__) and error.__cause__.code == code
    assert (error.line, error.col, error.provenance) == (0, 0, None)


def test_h04_blank_key_preserves_provenance_validation():
    with pytest.raises(KernelDiagnosticError) as caught:
        resolve('Float[1] a = host("")', {"": [1]})
    assert caught.value.code == "SCIENTIFIC_INPUT_PROVENANCE_ERROR"
    assert str(caught.value) == "input_id must not be empty"
    assert isinstance(caught.value.__cause__, scientific_input.ScientificInputValidationError)


def test_h05_tensor_arguments_and_real_merge(monkeypatch):
    tensors = []
    original = scientific_input.CoefficientTensor
    def record(**kwargs):
        tensor = original(**kwargs)
        tensors.append(tensor)
        return tensor
    monkeypatch.setattr(scientific_input, "CoefficientTensor", record)
    arrays, _ = resolve('Bool[1] a = host("x") Float[1] b = [2.0]', {"x": [True]})
    assert arrays == {"a": [True], "b": [2.0]}
    assert len(tensors) == 1
    tensor = tensors[0]
    assert (tensor.name, tensor.shape, tensor.dtype, tensor.values) == ("x", (1,), "Bool", (True,))
    assert tensor.provenance == scientific_input.InputProvenance("HostInputPort", "x")


def test_h05_merger_first_diagnostic_and_message(monkeypatch):
    monkeypatch.setattr(finite_binder, "merge_host_coefficient_arrays", lambda *args: (
        {"partial": [1]}, [{"code": "FIRST", "message": "first failure"},
                           {"code": "SECOND", "message": "second failure"}]
    ))
    with pytest.raises(KernelDiagnosticError) as caught:
        resolve('Float[1] a = host("x")', {"x": [1]})
    assert caught.value.code == "FIRST" and str(caught.value) == "first failure"
    assert caught.value.__cause__ is None


def test_h05_successful_merge_result_is_returned_without_copy(monkeypatch):
    expected = {"a": [1.0]}
    monkeypatch.setattr(finite_binder, "merge_host_coefficient_arrays", lambda *args: (expected, []))
    arrays, _ = resolve('Float[1] a = host("x")', {"x": [1]})
    assert arrays is expected


def test_h04_later_validation_precedes_earlier_missing_merge_error():
    with pytest.raises(KernelDiagnosticError) as caught:
        resolve('Float[1] a = host("missing") Float[1] b = host("bad")', {"bad": [float("nan")]})
    assert caught.value.code == "HOST_COEFFICIENT_VALUE_ERROR"
    assert isinstance(caught.value.__cause__, scientific_input.ScientificInputValidationError)


@pytest.mark.parametrize("port", [None, RecordingPort({"x": None})])
def test_h06_missing_port_or_none_fails_closed(port):
    with pytest.raises(KernelDiagnosticError) as caught:
        Evaluator(host_input=port)._resolve_host_coefficient_arrays(unit_for('Float[1] a = host("x")'))
    assert caught.value.code == "HOST_COEFFICIENT_MISSING"


def test_h06_same_key_later_shape_rejection():
    with pytest.raises(KernelDiagnosticError) as caught:
        resolve('Float[1] a = host("x") Float[2] b = host("x")', {"x": [1]})
    assert caught.value.code == "HOST_COEFFICIENT_SHAPE_ERROR"
    assert str(caught.value) == "Host coefficient `x` shape [1] does not match declared [2]"
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("first,second,raw,expected,leaf_type", [
    ("Bool", "Float", True, True, bool),
    ("Float", "Bool", 2, 2.0, float),
])
def test_h06_same_key_mixed_dtype_preserves_first_declaration(first, second, raw, expected, leaf_type):
    arrays, port = resolve(f'{first}[1] a = host("x") {second}[1] b = host("x")', {"x": [raw]})
    assert arrays == {"a": [expected], "b": [expected]} and port.reads == ["x"]
    assert type(arrays["b"][0]) is leaf_type


def test_h06_port_exception_is_not_converted():
    failure = RuntimeError("port unavailable")
    class RaisingPort:
        def get(self, name):
            raise failure
    with pytest.raises(RuntimeError) as caught:
        Evaluator(host_input=RaisingPort())._resolve_host_coefficient_arrays(
            unit_for('Float[1] a = host("x")')
        )
    assert caught.value is failure


def test_h07_live_hook_before_lowering_and_evaluator_owned_arrays(monkeypatch):
    evaluator = Evaluator()
    events = []
    arrays = {"a": [1.0]}
    def hook(unit):
        events.append("resolve")
        return arrays
    def lower(unit, *, host_arrays):
        events.append("lower")
        assert host_arrays is arrays and evaluator._resolved_host_arrays is arrays
        return {}, []
    monkeypatch.setattr(evaluator, "_resolve_host_coefficient_arrays", hook)
    monkeypatch.setattr(execution, "lower_finite_binder_operators", lower)
    execution._prepare_execution_context(evaluator, unit_for())
    assert events == ["resolve", "lower"] and evaluator._resolved_host_arrays is arrays


def test_h07_resolution_failure_stops_lowering(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("lowering after missing Host input")
    monkeypatch.setattr(execution, "lower_finite_binder_operators", forbidden)
    with pytest.raises(KernelDiagnosticError):
        execution._prepare_execution_context(Evaluator(), unit_for('Float[1] a = host("x")'))


def test_h08_cold_public_private_consumer_smoke():
    result = subprocess.run([sys.executable, "-c", '''
from types import SimpleNamespace
from compiler.staqex.runtime.evaluator import Evaluator, HostInputPort, KernelDiagnosticError
from compiler.staqex.runtime.evaluation.errors import KernelDiagnosticError as SharedError
from compiler.staqex.host_input_port import HostInputPort as SharedPort
assert HostInputPort is SharedPort and KernelDiagnosticError is SharedError
assert Evaluator()._resolve_host_coefficient_arrays(SimpleNamespace(main=None)) == {}
'''], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
