"""Call binding and frame entrypoints for the evaluator runtime."""

from __future__ import annotations

import cmath
import math
from collections import defaultdict
from typing import Any

from ...ast_nodes import (
    Attr, BinOp, Call, Coin, Expr, Hole, KetLit, Lambda, LitBool, LitFloat,
    LitInt, OpVar, Var,
)
from .context import EvaluatorContext
from .errors import KernelError
from ..joint import EPS, Joint, World, _coalesce
from ...continuous_field import ContinuousFieldValue
from ...stdlib import math_ops
from ..quantum_ops import cnot_bit, expect_pauli, expect_zz
from ..unitaries import apply_unitary_on_wires, hadamard, shift_position
from .values import evaluate_value


def _is_named_type(value: Any, type_name: str) -> bool:
    """Recognize evaluator-owned runtime values without importing the facade."""
    return type(value).__name__ == type_name


def resolve_call_target(context: EvaluatorContext, callee: Any) -> str | None:
    """Return the qualified call target without taking state ownership."""
    return context._expr_qualname(callee)


def bind_function_call(
    context: EvaluatorContext, joint: Joint, name: str, expr: Call, function: Any
) -> Joint:
    """Route a known user function through the existing local-frame binder."""
    return context._bind_user_fun(joint, [name], expr, function)


def bind_method_call(
    context: EvaluatorContext,
    joint: Joint,
    name: str,
    receiver: Any,
    method: Any,
    args: list[Any],
) -> Joint:
    """Route a known class method through the existing receiver binder."""
    return context._bind_method(joint, name, receiver, method, args)


def bind_call(context: EvaluatorContext, joint: Joint, name: str, expr: Call) -> Joint:
    callee = expr.callee
    classes = context._class_environment()
    structs = context._struct_environment()
    funs = context._function_environment()
    objects = context._object_environment()
    operators = context._operator_environment()

    # Class / struct construction reached via a free-function's own
    # `return Simple(args)` (or any other non-top-level classical
    # binding site) -- mirrors the top-level statement dispatch in
    # _run_unit_body and the classical-expression dispatch in
    # _eval_value, neither of which this function-body binding path
    # otherwise shares.
    if isinstance(callee, Var):
        q = resolve_call_target(context, callee) or callee.name
        if q in classes:
            objects[name] = context._construct_instance(q, expr)
            return joint
        if q in structs:
            objects[name] = context._construct_struct(q, expr)
            return joint

    # ADR 0123: form Partial when any `_` hole is present.
    if any(isinstance(a, Hole) for a in expr.args):
        fun_name: str | None = None
        if isinstance(callee, Var):
            fun_name = callee.name
        else:
            q = resolve_call_target(context, callee)
            if q is not None:
                fun_name = q
        if fun_name is None or fun_name not in funs:
            raise KernelError("Partial requires a known function callee")
        slots: list[Expr | None] = [
            None if isinstance(a, Hole) else a for a in expr.args
        ]
        objects[name] = context._make_partial_value(fun_name, slots)
        return joint

    # ADR 0123: Call on a bound Partial fills remaining holes.
    if isinstance(callee, Var) and callee.name in objects:
        partial = objects[callee.name]
        if _is_named_type(partial, "PartialValue"):
            filled = context._fill_partial(partial, list(expr.args))
            if _is_named_type(filled, "PartialValue"):
                objects[name] = filled
                return joint
            return bind_call(context, joint, name, filled)

    # ADR 0056: instance.method(args)
    if isinstance(callee, Attr):
        recv_expr = callee.obj
        method_name = callee.name
        q = resolve_call_target(context, callee)
        if q is not None and q in funs:
            return bind_function_call(context, joint, name, expr, funs[q])
        # Namespace-qualified struct constructors are represented as an
        # Attr (`D.Item(...)`), but are constructors rather than method
        # calls.  Resolve them before receiver/method dispatch so the
        # callable-plan path matches the value-evaluator path.
        if q is not None and q in structs:
            objects[name] = context._construct_struct(q, expr)
            return joint
        if q is not None and q in classes:
            raise KernelError(
                f"construct `{q}()` via Type-First "
                f"`{q} obj = {q}()`, not as a State expression"
            )
        inst = context._resolve_receiver_instance(recv_expr)
        if _is_named_type(inst, "ClassInstance"):
            cls = classes.get(inst.class_name) or classes.get(
                inst.class_name.split(".")[-1]
            )
            if cls is None:
                raise KernelError(f"unknown class `{inst.class_name}`")
            method = next(
                (m for m in cls.methods if m.name == method_name), None
            )
            if method is None:
                raise KernelError(
                    f"class `{inst.class_name}` has no method `{method_name}`"
                )
            return bind_method_call(context, joint, name, inst, method, list(expr.args))
        if _is_named_type(inst, "StructValue"):
            raise KernelError(
                f"struct `{inst.struct_name}` has no methods "
                f"(use class for methods)"
            )
        # Fall through to Math.* / map / etc.

    # User-module fn (ADR 0054)
    if isinstance(callee, Var) and callee.name in funs:
        return bind_function_call(context, joint, name, expr, funs[callee.name])

    # Math.sin(x) / Math.cos(x) / …
    if isinstance(callee, Attr):
        if isinstance(callee.obj, Var) and callee.obj.name == "Complex":
            if callee.name == "cis":
                if len(expr.args) != 1:
                    raise KernelError("Complex.cis requires (theta)")
                theta = float(evaluate_value(context, expr.args[0], {}))
                return Joint(
                    worlds=[World(assign={name: 0}, amp=cmath.exp(1j * theta))]
                )
            raise KernelError(f"unknown Complex.{callee.name}")
        if isinstance(callee.obj, Var) and callee.obj.name == "Math":
            if not math_ops.known_math_op(callee.name):
                raise KernelError(f"unknown Math.{callee.name}")
            if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
                raise KernelError(f"Math.{callee.name} expects one State variable")
            src = expr.args[0].name
            op = callee.name
            return joint.map_coord(src, name, lambda v: math_ops.apply_math(op, v))
        # extension: x.sin() → Math.sin(x)
        if isinstance(callee.obj, Var) and math_ops.known_math_op(callee.name):
            src = callee.obj.name
            op = callee.name
            return joint.map_coord(src, name, lambda v: math_ops.apply_math(op, v))
        # x.map(fn) — project is not a method (Hilbert project(state, k) only)
        if isinstance(callee.obj, Var) and callee.name == "map":
            src_expr = callee.obj
            if len(expr.args) < 1:
                raise KernelError("map requires a lambda")
            f = context._as_unary_fn(expr.args[0])
            return joint.map_coord(src_expr.name, name, f)
        if isinstance(callee.obj, Var) and callee.name == "project":
            raise KernelError(
                "use project(state, k) for Hilbert |k⟩⟨k|; "
                "method form state.project(pred) is removed"
            )
        raise KernelError(f"unsupported method {callee.name}")

    if isinstance(callee, Var):
        op = callee.name
    elif isinstance(callee, Coin):
        return joint.bind_split(name, {0: 0.5, 1: 0.5})
    else:
        raise KernelError(f"unsupported callee {type(callee)}")

    if op == "map":
        if len(expr.args) < 2:
            raise KernelError("map requires (src, fn)")
        src_expr, fn = expr.args[0], expr.args[1]
        if not isinstance(src_expr, Var):
            raise KernelError("map src must be a variable")
        f = context._as_unary_fn(fn)
        return joint.map_coord(src_expr.name, name, f)

    if op == "project":
        # Hilbert projector P̂ = |k⟩⟨k| on a wire (Lüders), then renorm.
        # Predicate filters are forbidden (classical programming smell).
        if len(expr.args) < 2:
            raise KernelError(
                "project requires (state, basisLabel) — Hilbert |k⟩⟨k|, "
                "not a predicate lambda"
            )
        src_expr, target = expr.args[0], expr.args[1]
        if not isinstance(src_expr, Var):
            raise KernelError("project src must be a state variable")
        if isinstance(target, Lambda):
            raise KernelError(
                "PREDICATE_PROJECTOR_ERROR: `project` is the Hilbert "
                "projector |k⟩⟨k|, not a classical filter. "
                "Write project(psi, 0) or project(psi, |0>)."
            )
        if isinstance(target, Var) and target.name in operators:
            # LISS-0431: `project psi onto P_F` -- a general (possibly
            # multi-term) Operator, e.g. LISS-0430's literal
            # $P_F=\sum_{x\in F}\lvert x\rangle\langle x\rvert$. Diagonal
            # projectors only for now (the confirmed target design
            # never needs anything else); scales each World's
            # amplitude by sqrt of the projector's diagonal entry at
            # that World's own coordinate value, matching
            # `bind_split`'s own probability->amplitude convention.
            projected = context._project_onto_operator(
                joint, src_expr.name, target.name
            )
        else:
            if isinstance(target, KetLit):
                bits = target.label
                if bits in {"0", "1"}:
                    label: Any = int(bits)
                elif set(bits) <= {"0", "1"} and bits != "":
                    label = int(bits, 2)
                else:
                    raise KernelError(
                        f"project onto |{bits}⟩: MVP supports "
                        "computational |0⟩/|1⟩ (and bitstrings) only"
                    )
            else:
                label = evaluate_value(context, target, {})
            projected = joint.project_coord(src_expr.name, lambda v, lab=label: v == lab)
        if projected.is_vacuum():
            return Joint.empty()
        # LISS-0431: `project` no longer renormalizes -- the result is
        # the literal, generally-unnormalized $P\lvert\psi\rangle$;
        # explicit renormalization is written at the call site via
        # `/ ||...||` (LISS-0426), matching the equation's own
        # separate $/\lVert\cdot\rVert$ factor instead of folding it
        # silently into every `project`.
        return projected.bind_pushforward(name, lambda a: a[src_expr.name])

    if op == "interfer":
        if not expr.args:
            return Joint.empty()
        # Sum complex amplitudes per result value (path interference).
        from collections import defaultdict

        amps: dict[Any, complex] = defaultdict(complex)
        for arg in expr.args:
            if isinstance(arg, Var):
                for val, c in joint.amplitude_marginal(arg.name).items():
                    amps[val] += c
            elif isinstance(arg, (LitInt, LitFloat, LitBool)):
                amps[context._lit(arg)] += complex(1.0, 0.0)
            else:
                for w in joint.worlds:
                    val = evaluate_value(context, arg, w.assign)
                    amps[val] += w.amp
        # Drop cancelled bins; renormalize Born measure (SV-07 mixture).
        alive = {v: c for v, c in amps.items() if abs(c) ** 2 > EPS}
        if not alive:
            return Joint.empty()
        total = sum(abs(c) ** 2 for c in alive.values())
        scale = 1.0 / cmath.sqrt(total)
        out = [
            World(assign={name: val}, amp=c * scale) for val, c in alive.items()
        ]
        return Joint(worlds=_coalesce(out))

    if op == "phase":
        # phase(src, theta) or phase(src, theta, only_value)
        # ADR 0060: θ / only resolve against scalars ∪ objects ∪ assign
        if len(expr.args) < 2 or not isinstance(expr.args[0], Var):
            raise KernelError("phase requires (src, theta[, only])")
        src = expr.args[0].name
        theta = float(evaluate_value(context, expr.args[1], {}))
        only = None
        if len(expr.args) >= 3:
            only = evaluate_value(context, expr.args[2], {})
        return joint.phase_copy(src, name, theta, only=only)

    if op in {"grover_diffuse", "diffuse"}:
        # grover_diffuse(src) — Grover inversion about mean
        if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
            raise KernelError("grover_diffuse requires (src)")
        return joint.diffuse_copy(expr.args[0].name, name)

    if op == "cis":
        # cis(theta): unit |0⟩ with amplitude e^{iθ}
        if len(expr.args) != 1:
            raise KernelError("cis requires (theta)")
        theta = float(evaluate_value(context, expr.args[0], {}))
        return Joint(worlds=[World(assign={name: 0}, amp=cmath.exp(1j * theta))])

    if op == "cnot":
        # cnot(ctrl, tgt) — unitary |c,t⟩↦|c,t⊕c⟩; bind result as new tgt wire
        if len(expr.args) != 2:
            raise KernelError("cnot requires (ctrl, tgt)")
        if not isinstance(expr.args[0], Var) or not isinstance(expr.args[1], Var):
            raise KernelError("cnot args must be state variables")
        ctrl_n = expr.args[0].name
        tgt_n = expr.args[1].name
        return joint.bind_pushforward(
            name, lambda a: cnot_bit(a[ctrl_n], a[tgt_n])
        )

    if op == "apply":
        # apply(U, w0[, w1, …]) — unitary on wires (H⊗I…); U = Operator | Hadamard | Pauli
        return context._bind_apply(joint, name, expr)

    if op in {"capply", "controlled"}:
        # capply(ctrl[, …], U, tgt[, …]) — Cⁿ(U) on |1…1⟩
        return context._bind_capply(joint, name, expr, op_label=op)

    if op == "ocapply":
        # ocapply(ctrl[, …], U, tgt[, …]) — all open (|0⟩) controls
        return context._bind_capply(
            joint, name, expr, force_all_open=True, op_label="ocapply"
        )

    if op == "toffoli":
        # toffoli(c0, c1, tgt) — sugar for capply(c0, c1, X, tgt)
        if len(expr.args) != 3:
            raise KernelError("toffoli requires (ctrl0, ctrl1, tgt)")
        if not all(isinstance(a, Var) for a in expr.args):
            raise KernelError("toffoli args must be state variables")
        sp = expr.span
        synthetic = Call(
            callee=Var(name="capply", span=sp),
            args=[
                expr.args[0],
                expr.args[1],
                Var(name="X", span=sp),
                expr.args[2],
            ],
            span=sp,
        )
        return context._bind_capply(joint, name, synthetic)

    if op == "hadamard":
        # hadamard(w) — sugar for apply(Hadamard, w)
        if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
            raise KernelError("hadamard requires (wire)")
        wire = expr.args[0].name
        try:
            updated = apply_unitary_on_wires(joint, [wire], hadamard())
        except ValueError as e:
            raise KernelError(str(e)) from e
        if name == wire:
            return updated
        return updated.bind_pushforward(name, lambda a, w=wire: a[w])

    if op in {"walk_shift", "shift"}:
        # walk_shift(coin, pos) — DTQW conditional translation
        if len(expr.args) != 2:
            raise KernelError("walk_shift requires (coin, pos)")
        if not isinstance(expr.args[0], Var) or not isinstance(expr.args[1], Var):
            raise KernelError("walk_shift args must be state variables")
        coin_n = expr.args[0].name
        pos_n = expr.args[1].name
        return joint.bind_pushforward(
            name, lambda a: shift_position(a[coin_n], a[pos_n])
        )

    if op == "tensor":
        raise KernelError("use `(a, b) = left *|* right`")

    if op == "trace_out":
        # trace_out(coord) — partial trace / discard subsystem coordinate
        if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
            raise KernelError("trace_out requires (coordVar)")
        coord = expr.args[0].name
        trimmed = joint.trace_out(coord)
        # Placeholder classical bind; remaining coordinates stay measurable
        return trimmed.bind_const(name, 0)

    if op == "expect":
        # expect(O, psi) — single-qubit ⟨P⟩
        # expect(ZZ, a, b) — two-qubit ⟨Z⊗Z⟩ (Bell correlation; no collapse)
        if len(expr.args) == 2 and isinstance(expr.args[1], Var):
            op_name = context._operator_name(expr.args[0])
            if op_name.upper() == "ZZ":
                raise KernelError("expect(ZZ, …) requires two qubit variables")
            src = expr.args[1].name
            amps = joint.amplitude_marginal(src)
            a0 = amps.get(0, 0j)
            a1 = amps.get(1, 0j)
            try:
                val = expect_pauli(op_name, a0, a1)
            except ValueError as e:
                raise KernelError(str(e)) from e
            # Non-destructive: bind scalar onto existing joint worlds
            return joint.bind_const(name, float(val))
        if (
            len(expr.args) == 3
            and isinstance(expr.args[1], Var)
            and isinstance(expr.args[2], Var)
        ):
            op_name = context._operator_name(expr.args[0])
            if op_name.upper() != "ZZ":
                raise KernelError(
                    f"two-qubit expect supports ZZ only, got `{op_name}`"
                )
            try:
                val = expect_zz(
                    joint.worlds, expr.args[1].name, expr.args[2].name
                )
            except ValueError as e:
                raise KernelError(str(e)) from e
            return joint.bind_const(name, float(val))
        raise KernelError(
            "expect requires (operator, stateVar) or (ZZ, qubitA, qubitB)"
        )

    if op == "occupation":
        # occupation(psi, k) — Born weight |⟨k|ψ⟩|² on Int site / Fock label
        if len(expr.args) != 2 or not isinstance(expr.args[0], Var):
            raise KernelError("occupation requires (stateVar, siteIndex)")
        src = expr.args[0].name
        k = evaluate_value(context, expr.args[1], {})
        if not isinstance(k, int):
            try:
                k = int(k)
            except (TypeError, ValueError) as e:
                raise KernelError("occupation site index must be Int") from e
        amps = joint.amplitude_marginal(src)
        val = float(abs(amps.get(k, 0j)) ** 2)
        return joint.bind_const(name, val)

    if op == "Coin":
        return joint.bind_split(name, {0: 0.5, 1: 0.5})
    if op == "Vacuum":
        # vacuum() = |0⟩ (Fock / computational ground), NOT empty support
        return joint.bind_pushforward(name, lambda a: 0)
    if op == "empty":
        # empty support (destructive interference / null joint)
        return Joint.empty()
    if op == "Dirac":
        if not expr.args:
            raise KernelError("dirac requires an argument (point mass δ_c)")
        return joint.bind_pushforward(name, lambda a: evaluate_value(context, expr.args[0], a))
    if op == "finiteize":
        # ADR 0185 Lane A: finiteize(lo, hi, n_bins, n_samples[, seed])
        # Host equal-width histogram of uniform continuous draws on [lo, hi).
        # Result is ordinary finite State (no mid-program Continuous type).
        # ADR 0204 / LISS-0401: a Continuous first argument dispatches to
        # the second overload instead -- discriminated by the first
        # arg's bound value, not by arity (both forms take 4-5 args).
        if (
            expr.args
            and isinstance(expr.args[0], Var)
            and isinstance(objects.get(expr.args[0].name), ContinuousFieldValue)
        ):
            return context._bind_finiteize_continuous(joint, name, expr)
        return context._bind_finiteize(joint, name, expr)
    if op == "field_from_host":
        # ADR 0204 / LISS-0399: Continuous injection -- never touches the
        # Joint; the Kernel only ever holds an opaque handle.
        return context._bind_field_from_host(joint, name, expr)
    if op == "weight":
        # ADR 0204 / LISS-0400: pointwise composition -- Kernel-side
        # bookkeeping only, no math evaluated here.
        return context._bind_continuous_compose(joint, name, expr, op_name="weight", arity=(2, 3))
    if op == "mask":
        return context._bind_continuous_compose(joint, name, expr, op_name="mask", arity=(2, 2))
    if op == "prepare_selection":
        # LISS-0324: prepare_selection(n) -- equal superposition over all
        # 2**n n-candidate selection patterns. Candidate identity never
        # crosses into the Kernel; only the finite width does.
        return context._bind_prepare_selection(joint, name, expr)

    if op == "wavepacket":
        # wavepacket(xmin, xmax, n, x0, sigma) — Gaussian on a uniform grid
        if len(expr.args) != 5:
            raise KernelError(
                "wavepacket requires (xmin, xmax, n, x0, sigma)"
            )
        xmin = float(evaluate_value(context, expr.args[0], {}))
        xmax = float(evaluate_value(context, expr.args[1], {}))
        n_raw = evaluate_value(context, expr.args[2], {})
        if type(n_raw) is not int:
            raise KernelError("wavepacket n must be Int")
        n = n_raw
        x0 = float(evaluate_value(context, expr.args[3], {}))
        sigma = float(evaluate_value(context, expr.args[4], {}))
        if n < 2:
            raise KernelError("wavepacket needs n >= 2")
        if sigma <= 0:
            raise KernelError("wavepacket sigma must be positive")
        if xmax <= xmin:
            raise KernelError("wavepacket requires xmax > xmin")
        dx = (xmax - xmin) / float(n)
        xs = [xmin + i * dx for i in range(n)]
        # ψ ∝ exp(-(x-x0)²/(4σ²)) so |ψ|² has std σ
        import math as _math

        raw = [
            _math.exp(-((x - x0) ** 2) / (4.0 * sigma * sigma)) for x in xs
        ]
        norm2 = sum(a * a for a in raw)
        if norm2 <= EPS:
            raise KernelError("wavepacket amplitudes vanished")
        dist = {xs[i]: (raw[i] * raw[i]) / norm2 for i in range(n)}
        return joint.bind_split(name, dist)
    if math_ops.known_math_op(op):
        if len(expr.args) != 1 or not isinstance(expr.args[0], Var):
            raise KernelError(f"{op} expects one State variable")
        src = expr.args[0].name
        return joint.map_coord(src, name, lambda v: math_ops.apply_math(op, v))

    if op == "inner":
        return context._bind_inner(joint, name, expr)
    if op == "outer":
        raise KernelError(
            "outer must be bound as `Operator … = outer(…)`, not a State Call"
        )

    raise KernelError(f"unknown function `{op}`")
