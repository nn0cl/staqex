"""O01–O05: actual checker mechanics, not a second implementation."""

import ast
from pathlib import Path
import sys

import pytest

from compiler.staqex import typecheck
from compiler.staqex.ast_nodes import (
    IndexDomain, RevDomain, TypeRef, OpBinder, OpBin, OpCall, OpIndexed,
    OpLit, OpVar, Span,
)

S = Span(7, 9)
D = Span(11, 13)


def ref(name, *bounds):
    return TypeRef(name, [TypeRef(str(value)) for value in bounds])


def binder(domain):
    return OpBinder("sum", "i", domain, OpVar("body", S), S)


def mechanics():
    checker = typecheck.TypeChecker()
    events = []
    checker._check_operator_expr = lambda expr: events.append(("walk", expr, checker._binder_depth, checker.env.get("i")))
    checker._require_full_rank_coeff = lambda expr: events.append(("rank", expr, checker._binder_depth, checker.env.get("i")))
    return checker, events


@pytest.mark.parametrize("domain,code,message", [
    (ref("Basis", -1), "BINDER_DOMAIN_ERROR", "`Basis<N>` binder domain requires a static non-negative integer size"),
    (ref("Basis", 0), "EMPTY_BINDER_DOMAIN_WARNING", "Basis binder domain is empty; using the fold identity"),
    (ref("Basis", 4), "BINDER_DOMAIN_ERROR", "Basis binder domain exceeds the static register shape"),
    (ref("Other"), "BINDER_DOMAIN_ERROR", "binder domain `Other` is not a finite `Index` or `Basis` range; other carriers remain deferred"),
    (ref("Index", 0), "BINDER_DOMAIN_ERROR", "`Index<N>` or inclusive `Index<start..end>` requires static bounds"),
    (ref("Index", 2, 1), "EMPTY_BINDER_DOMAIN_WARNING", "inclusive binder range is empty; using the fold identity"),
    (ref("Index", 0, 3), "BINDER_DOMAIN_ERROR", "inclusive binder range exceeds the static register shape"),
])
def test_o02_static_domain_diagnostic_and_continued_walk(domain, code, message):
    checker, events = mechanics()
    checker.env["r"] = typecheck.Ty("Register", "R")
    checker.semantic_values["r"] = 3
    calls = []
    checker._ty_from_ref = lambda value: calls.append(value) or typecheck.Ty("Meta", value.name)
    expr = binder(domain)
    assert checker._legacy_check_operator(expr) is None
    assert checker.diagnostics == [dict(code=code, line=7, col=9, message=message)]
    assert calls[0] is domain
    assert len(calls) == (2 if domain.name == "Basis" and int(domain.args[0].name) >= 0 else 1)
    assert [e[0] for e in events] == ["walk", "rank"]


@pytest.mark.parametrize("domain", [ref("Basis", 3), ref("Index", 3), ref("Index", 0, 2)])
def test_o02_static_positive_neighbors_and_register_capacity_filter(domain):
    checker, _ = mechanics()
    checker.env.update(r=typecheck.Ty("Register", "R"), nonregister=typecheck.Ty("Meta", "Index"))
    checker.semantic_values.update(r=3, nonregister=0, missing=0)
    checker._legacy_check_operator(binder(domain))
    assert checker.diagnostics == []


@pytest.mark.parametrize("kind,payload,expected", [
    (None, None, "BINDER_DOMAIN_ERROR"), ("Execution", "Wire", "PHASE_TYPE_VISIBILITY_ERROR"),
    ("State", "Q", "BINDER_DOMAIN_ERROR"), ("Meta", "Index", None),
    ("Discrete", "D", None), ("State", "Set", None), ("Classical", "Set", None),
])
@pytest.mark.parametrize("size", [1_000_000, 1_000_001])
def test_o02_named_domain_resource_boundary_is_independent(kind, payload, expected, size):
    checker, events = mechanics()
    if kind:
        checker.env["F"] = typecheck.Ty(kind, payload)
    checker.semantic_values["F"] = size
    checker._legacy_check_operator(binder(OpVar("F", D)))
    codes = ([expected] if expected else []) + (["BINDER_RESOURCE_ERROR"] if size > 1_000_000 else [])
    assert [d["code"] for d in checker.diagnostics] == codes
    assert all((d["line"], d["col"]) == (11, 13) for d in checker.diagnostics)
    if expected == "PHASE_TYPE_VISIBILITY_ERROR":
        assert checker.diagnostics[0]["message"] == f"execution carrier `{checker.env['F']}` cannot be a theory domain"
    elif expected:
        assert checker.diagnostics[0]["message"] == ("unknown finite binder domain `F`" if kind is None else "`F` is not a finite semantic domain")
    if size > 1_000_000:
        assert checker.diagnostics[-1]["message"] == "finite binder expansion exceeds the Kernel resource budget"
    assert len(events) == 2


@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("prior", ["absent", "none", "ty"])
def test_o03_index_expression_two_fresh_types_and_restoration(reverse, prior, monkeypatch):
    checker, events = mechanics()
    previous = typecheck.Ty("Meta", "Old")
    if prior != "absent":
        checker.env["i"] = previous if prior == "ty" else None
    domain = IndexDomain(OpLit(0, S), OpLit(2, S), S)
    if reverse:
        domain = RevDomain(domain, S)
    checker._check_index_domain_expr = lambda value: events.append(("domain", value, checker._binder_depth, checker.env.get("i")))
    actual_ty = typecheck.Ty
    values = []

    def factory(*args, **kwargs):
        value = actual_ty(*args, **kwargs)
        values.append(value)
        return value

    monkeypatch.setattr(typecheck, "Ty", factory)
    checker._legacy_check_operator(binder(domain))
    assert [e[0] for e in events] == ["domain", "walk", "rank"]
    assert events[0][2] == 0
    assert len(values) == 2 and values[0] is not values[1]
    assert all(type(v) is actual_ty and v.kind == "Meta" and v.payload == "Index" for v in values)
    assert events[1][2:] == (1, values[1]) == events[2][2:]
    assert checker._binder_depth == 0
    assert (checker.env.get("i") is previous) if prior == "ty" else "i" not in checker.env


def test_o03_live_map_replacement_and_nested_override_recursion():
    class Recording(typecheck.TypeChecker):
        def _check_operator_expr(self, expr):
            seen.append((expr, self._binder_depth, self.env.get("i")))
            return super()._check_operator_expr(expr)

    seen = []
    checker = Recording()
    inner = binder(ref("Index", 2))
    outer = binder(ref("Index", 3))
    outer.body = inner
    checker._require_full_rank_coeff = lambda expr: None
    checker._legacy_check_operator(outer)
    assert [depth for _, depth, _ in seen] == [1, 2]
    assert "i" not in checker.env
    checker, _ = mechanics()
    replacement = {"i": typecheck.Ty("Meta", "Callback")}
    checker._check_operator_expr = lambda expr: setattr(checker, "env", replacement)
    checker._legacy_check_operator(binder(ref("Index", 2)))
    assert checker.env is replacement and "i" not in replacement


class Abort(BaseException):
    pass


@pytest.mark.parametrize("failure", [RuntimeError, Abort])
@pytest.mark.parametrize("where", ["walk", "rank", "domain", "append", "get", "restore"])
def test_o04_failure_timing_preserves_baseline_without_added_cleanup(where, failure, monkeypatch):
    checker, events = mechanics()
    error = failure("same instance")

    def fail(*args, **kwargs):
        raise error

    domain = ref("Index", 2)
    if where == "walk":
        checker._check_operator_expr = fail
    elif where == "rank":
        checker._require_full_rank_coeff = fail
    elif where == "domain":
        checker._ty_from_ref = fail
    elif where == "append":
        class Diagnostics(list):
            append = staticmethod(fail)
        checker.diagnostics = Diagnostics()
        domain = ref("Other")
    elif where == "get":
        class BrokenGet(dict):
            get = staticmethod(fail)
        checker.env = BrokenGet()
    else:
        class BrokenPop(dict):
            pop = staticmethod(fail)
        checker.env = BrokenPop()
    with pytest.raises(failure) as raised:
        checker._legacy_check_operator(binder(domain))
    assert raised.value is error
    assert checker._binder_depth == 0
    assert ("i" in checker.env) == (where in {"walk", "rank", "restore"})
    assert [e[0] for e in events] == ({"rank": ["walk"], "restore": ["walk", "rank"]}.get(where, []))


def operator_type_sites(checker):
    """Locate actual owner call sites before/after the approved extraction."""
    code = checker._legacy_check_operator.__func__.__code__
    tree = ast.parse(Path(code.co_filename).read_text())
    method = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
                  and n.name == code.co_name and n.lineno == code.co_firstlineno)
    sites = sorted(n.lineno for n in ast.walk(method) if isinstance(n, ast.Call)
                   and ((isinstance(n.func, ast.Name) and n.func.id == "Ty")
                        or (isinstance(n.func, ast.Attribute)
                            and isinstance(n.func.value, ast.Name)
                            and n.func.value.id == "self"
                            and n.func.attr == "_operator_index_type")))
    assert len(sites) == 2
    return code, sites


@pytest.mark.parametrize("prior", ["absent", "none", "ty"])
@pytest.mark.parametrize("failure", [RuntimeError, Abort])
@pytest.mark.parametrize("path,attempt,site", [
    ("type-ref", 1, 1), ("index-domain", 1, 0), ("index-domain", 2, 1),
])
def test_o04_factory_failure_reaches_named_operator_site(path, attempt, site, failure, prior, monkeypatch):
    checker, events = mechanics()
    real_ty = typecheck.Ty
    previous = real_ty("Meta", "Previous")
    converted = real_ty("Meta", "Index")
    if prior != "absent":
        checker.env["i"] = previous if prior == "ty" else None
    checker._binder_depth = 2
    original_env = checker.env
    before = dict(original_env)
    algorithm, sites = operator_type_sites(checker)
    error = failure("operator constructor failure")
    calls = []

    def convert(domain):
        events.append(("convert", domain, checker._binder_depth, checker.env.get("i")))
        return converted  # No call to the globally patched constructor.

    checker._ty_from_ref = convert
    checker._check_index_domain_expr = lambda domain: events.append(("domain", domain, checker._binder_depth, checker.env.get("i")))
    domain = ref("Index", 2) if path == "type-ref" else IndexDomain(OpLit(0, S), OpLit(2, S), S)

    def construct(*args, **kwargs):
        caller = sys._getframe(1)
        if caller.f_code.co_name == "_operator_index_type":
            caller = caller.f_back
        assert caller.f_code is algorithm, "constructor failed in a different callback"
        calls.append(caller.f_lineno)
        assert args == ("Meta", "Index", typecheck.DIMLESS) and kwargs == {}
        events.append(("construct", len(calls), checker._binder_depth, checker.env.get("i")))
        if len(calls) == attempt:
            raise error
        return real_ty(*args, **kwargs)

    monkeypatch.setattr(typecheck, "Ty", construct)
    with pytest.raises(failure) as raised:
        checker._legacy_check_operator(binder(domain))
    assert raised.value is error
    assert calls == ([sites[site]] if path == "type-ref" else sites[:attempt])
    expected = [("convert" if path == "type-ref" else "domain", domain, 2, before.get("i"))]
    expected += [("construct", number, 2, before.get("i")) for number in range(1, attempt + 1)]
    assert events == expected  # No body/rank visit or premature binding.
    assert checker._binder_depth == 2
    assert checker.env is original_env and checker.env == before
    if prior == "ty":
        assert checker.env["i"] is previous


@pytest.mark.parametrize("depth", [0, 1, 2])
def test_o05_binary_order_and_positive_depth_only(depth):
    checker, events = mechanics()
    checker._binder_depth = depth
    expr = OpBin("+", OpVar("a", S), OpVar("b", S), S)
    checker._legacy_check_operator(expr)
    assert [(e[0], e[1]) for e in events] == [("walk", expr.lhs), ("walk", expr.rhs)] + ([("rank", expr.lhs), ("rank", expr.rhs)] if depth else [])


@pytest.mark.parametrize("base,exempt", [("c", False), ("create", True), ("annihilate", True), ("coeff", True)])
def test_o05_indexed_coefficient_exemptions_execution_index_and_order(base, exempt):
    checker, events = mechanics()
    checker._binder_depth = 1
    checker.float_arrays["coeff"] = (2,)
    checker.env["x"] = typecheck.Ty("Execution", "Wire")
    expr = OpIndexed(OpVar(base, S), OpVar("x", D), S)
    checker._legacy_check_operator(expr)
    assert [(e[0], e[1]) for e in events] == [("walk", expr.base), ("walk", expr.index)]
    expected = ([] if exempt else [dict(code="BINDER_LOWERING_UNSUPPORTED", line=7, col=9, message="indexed coefficient `c[…]` requires a `Float[N]…` binding (or a second-quantized atom)")])
    assert checker.diagnostics == expected + [dict(code="PHASE_TYPE_VISIBILITY_ERROR", line=11, col=13, message="execution carrier cannot index a theory operator")]


@pytest.mark.parametrize("active,base,expected", [(None, "Z", []), ("s", "r", []), ("s", "Z", ["MULTI_REGISTER_INDEX_AMBIGUOUS"])])
def test_o05_register_qualified_site_neighbors(active, base, expected):
    checker, _ = mechanics()
    checker._active_register_set = active
    checker.system_registers["s"] = (("r", 2), ("other", 2))
    checker._legacy_check_operator(OpIndexed(OpVar(base, S), OpLit(0, D), S))
    assert [d["code"] for d in checker.diagnostics] == expected
    if expected:
        assert checker.diagnostics == [dict(code=expected[0], line=11, col=13, message="multi-register operators require a register-qualified site")]


@pytest.mark.parametrize("active,name,expected", [(None, "missing", False), ("s", "r", False), ("s", "missing", True)])
def test_o05_nested_register_identity(active, name, expected):
    checker, _ = mechanics()
    checker._active_register_set = active
    checker.system_registers["s"] = (("r", 2),)
    index = OpIndexed(OpVar(name, S), OpLit(0, S), D)
    checker._legacy_check_operator(OpIndexed(OpVar("Z", S), index, S))
    assert checker.diagnostics == ([dict(code="UNKNOWN_REGISTER_ID", line=11, col=13, message="unknown register `missing` in acting space")] if expected else [])


@pytest.mark.parametrize("name", ["I", "X", "Y", "Z", "Measure", "log", "write", "send", "custom"])
def test_o05_call_diagnostics_precede_ordered_argument_recursion(name):
    checker, events = mechanics()
    args = [OpVar("a", S), OpVar("b", D)]
    seen = []
    checker._check_operator_expr = lambda expr: seen.append((expr, list(checker.diagnostics)))
    checker._legacy_check_operator(OpCall(name, args, S))
    expected = []
    if name in {"I", "X", "Y", "Z"}:
        expected = [dict(code="RETIRED_OPERATOR_INDEX_SYNTAX", line=7, col=9, message=f"`{name}(…)` is retired operator-index syntax; write `{name}[…]`")]
    elif name != "custom":
        expected = [dict(code="MATHEMATICAL_BINDER_EFFECT_ERROR", line=7, col=9, message=f"`{name}` is not allowed in a mathematical binder")]
    assert checker.diagnostics == expected
    assert seen == [(arg, expected) for arg in args]
    assert events == []


def test_o01_unmatched_node_returns_none_without_callbacks():
    checker, events = mechanics()
    assert checker._legacy_check_operator(object()) is None
    assert events == [] and checker.diagnostics == []
