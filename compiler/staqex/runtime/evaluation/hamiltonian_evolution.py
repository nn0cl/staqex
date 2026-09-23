"""Hamiltonian evolution for evaluator evolution."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from ...ast_nodes import (
    EvolveExpr,
    OpAttr,
    OpBin,
    OpBinder,
    OpCall,
    OpGridQuad,
    OpHop,
    OpIdentity,
    OpIndexed,
    OpLit,
    OpNumber,
    OpPauli,
    OpPow,
    OpQuadrature,
    OpVar,
    Var,
)
from ...continuous_lowering import GridHamiltonian, GridHamiltonianRef
from ...dimensions import UNIT_TABLE, to_canonical_magnitude
from .context import EvaluatorContext
from .errors import KernelDiagnosticError, KernelError
from ..joint import EPS, Joint, World, _coalesce
from ..op_attr_elaboration import OpAttrElaborationError, materialize_op_attrs


def _canonical_duration(context: EvaluatorContext, expr: EvolveExpr) -> float:
    # ADR 0195: evolve's duration must resolve to a real Time unit --
    # a bare dimensionless duration can no longer be silently treated
    # as "already in seconds" under the old hbar=1 convention.
    # LISS-0357: resolve via the already-general _eval_value_with_unit
    # (Var, struct-field Attr via ADR 0174 field_units, and
    # literal-suffix Attr) instead of a bare-Var-only check, so
    # `evolve ... for config.duration` and `evolve ... for 0.25.fs`
    # are recognized the same as a pre-bound Time variable.
    t_raw_val, duration_unit = context._eval_value_with_unit(expr.duration, {})
    if UNIT_TABLE.get(duration_unit, (None, None))[0] != "Time":
        raise KernelDiagnosticError(
            "EVOLVE_UNRESOLVED_UNIT_ERROR",
            "evolve duration must resolve to a real Time unit (e.g. "
            "a Float scalar declared with a `s`/`ps`/`ns`/`fs` suffix) "
            "-- a bare dimensionless duration is not accepted (ADR 0195)",
            line=expr.span.line,
            col=expr.span.col,
        )

    t_raw = float(t_raw_val)
    # ADR 0195: bare unit suffixes stay in their declared unit unless
    # explicitly `to`-converted (dimensions.py convention) -- so a
    # duration declared as `X.fs` must still be canonicalized to real
    # seconds here before use, regardless of whether the source also
    # wrote an explicit `to s`.
    t, _canon_duration_unit = to_canonical_magnitude(t_raw, duration_unit)
    return t


def _legacy_single_pauli_evolve(
    joint: Joint, names: list[str], hop: Var, duration: float
) -> Joint:
    from ..quantum_ops import apply_u2, pauli_u

    try:
        u = pauli_u(hop.name, duration)
    except ValueError as e:
        raise KernelError(str(e)) from e
    src = names[0]
    amps = joint.amplitude_marginal(src)
    if any(v not in (0, 1) for v in amps):
        raise KernelError(
            f"hamiltonian `{hop.name}` expects qubit support {{0,1}}, got {sorted(amps)}"
        )
    # Preserve sibling/classical coordinates by applying the gate per slice.
    groups: dict[tuple, list[World]] = defaultdict(list)
    for world in joint.worlds:
        if src not in world.assign:
            continue
        if world.assign[src] not in (0, 1):
            raise KernelError(
                f"hamiltonian `{hop.name}` expects qubit support {{0,1}}, "
                f"got {world.assign[src]!r}"
            )
        key = tuple(
            sorted((key, value) for key, value in world.assign.items() if key != src)
        )
        groups[key].append(world)

    out: list[World] = []
    for key, worlds in groups.items():
        a0 = a1 = 0j
        phase0: dict[str, complex] = {}
        phase1: dict[str, complex] = {}
        for world in worlds:
            if world.assign[src] == 0:
                a0 += world.amp
                phase0 = dict(world.coord_phase)
            else:
                a1 += world.amp
                phase1 = dict(world.coord_phase)
        b0, b1 = apply_u2(a0, a1, u)
        base = dict(key)
        if abs(b0) ** 2 > EPS:
            out.append(World(assign={**base, src: 0}, amp=b0, coord_phase=phase0))
        if abs(b1) ** 2 > EPS:
            out.append(World(assign={**base, src: 1}, amp=b1, coord_phase=phase1))
    return Joint(worlds=_coalesce(out))


def _resolve_hamiltonian(context: EvaluatorContext, hop: Any) -> tuple[Any, int | None]:
    from ..hamiltonian import op_n_qubits

    if isinstance(hop, Var):
        if hop.name not in context.operators:
            raise KernelError(f"unknown Operator / Hamiltonian `{hop.name}`")
        op_ast = context.operators[hop.name]
        declared_space = context.operator_spaces.get(hop.name)
    elif isinstance(
        hop,
        (
            OpPauli,
            OpNumber,
            OpQuadrature,
            OpGridQuad,
            OpHop,
            OpLit,
            OpBin,
            OpPow,
            OpVar,
            OpAttr,
            OpIndexed,
            OpBinder,
            OpIdentity,
            OpCall,
        ),
    ):
        op_ast = hop
        declared_space = None
    else:
        raise KernelError("hamiltonian must be Operator name or Pauli literal")

    try:
        op_ast = materialize_op_attrs(
            op_ast, context.objects, operators=context.operators
        )
        if isinstance(op_ast, GridHamiltonianRef):
            return op_ast, declared_space
        nq = (
            declared_space
            if declared_space is not None
            else op_n_qubits(op_ast, context.operators, context.scalars)
        )
    except (OpAttrElaborationError, ValueError) as exc:
        raise KernelError(str(exc)) from exc
    return op_ast, nq


def _evolve_non_qubit_basis(
    context: EvaluatorContext,
    joint: Joint,
    names: list[str],
    op_ast: Any,
    basis_size: int,
    duration: float,
) -> Joint | None:
    if basis_size == 0:
        from ..hamiltonian import compile_hamiltonian, hop_basis_dim
        from ..matrix import apply_mat, expm_ih

        if len(names) != 1:
            raise KernelError("Fock Hamiltonian evolve requires a single bind name")
        source = names[0]
        amplitudes = joint.amplitude_marginal(source)
        levels = sorted(amplitudes)
        if not levels or any(not isinstance(level, int) or level < 0 for level in levels):
            raise KernelError("Fock evolve expects non-negative Int levels")
        dimension = max(
            max(levels) + 1,
            hop_basis_dim(op_ast, context.operators, context.scalars),
            2,
        )
        try:
            hamiltonian = compile_hamiltonian(
                op_ast,
                env=context.operators,
                scalars=context.scalars,
                n_qubits=0,
                fock_dim=dimension,
            )
            unitary = expm_ih(hamiltonian, duration)
        except ValueError as exc:
            raise KernelError(str(exc)) from exc
        vector = [amplitudes.get(level, 0j) for level in range(dimension)]
        evolved = apply_mat(unitary, vector)
        worlds = [
            World(assign={source: level}, amp=amplitude)
            for level, amplitude in enumerate(evolved)
            if abs(amplitude) ** 2 > EPS
        ]
        return Joint(worlds=_coalesce(worlds))

    if basis_size < 0:
        from ..hamiltonian import compile_hamiltonian
        from ..matrix import apply_mat, expm_ih

        if len(names) != 1:
            raise KernelError("grid Hamiltonian evolve requires a single bind name")
        source = names[0]
        amplitudes = joint.amplitude_marginal(source)
        coordinates = sorted(amplitudes, key=float)
        if not coordinates or any(
            not isinstance(coordinate, (int, float)) for coordinate in coordinates
        ):
            raise KernelError("grid evolve expects Float (or Int) abscissae")
        grid_coordinates = [float(coordinate) for coordinate in coordinates]
        try:
            hamiltonian = compile_hamiltonian(
                op_ast,
                env=context.operators,
                scalars=context.scalars,
                n_qubits=-1,
                grid_xs=grid_coordinates,
            )
            unitary = expm_ih(hamiltonian, duration)
        except ValueError as exc:
            raise KernelError(str(exc)) from exc
        vector = [amplitudes[coordinate] for coordinate in coordinates]
        evolved = apply_mat(unitary, vector)
        worlds = [
            World(assign={source: coordinates[index]}, amp=amplitude)
            for index, amplitude in enumerate(evolved)
            if abs(amplitude) ** 2 > EPS
        ]
        return Joint(worlds=_coalesce(worlds))

    return None


def hamiltonian_evolve_one_step(
    context: EvaluatorContext, joint: Joint, names: list[str], expr: EvolveExpr
) -> Joint:
    duration = _canonical_duration(context, expr)
    hop = expr.hamiltonian
    assert hop is not None

    # Legacy single-name Pauli string: evolve psi under X for t
    if (
        isinstance(hop, Var)
        and hop.name.upper() in {"I", "X", "Y", "Z"}
        and len(names) == 1
    ):
        # LISS-0112 Slice B: Identity is a no-op on any computational level
        # (matches qubit `pauli_u(I)` = I; enables D=3 |2⟩ support).
        if hop.name.upper() in {"I", "ID", "IDENTITY"}:
            return joint
        return _legacy_single_pauli_evolve(joint, names, hop, duration)

    op_ast, nq = _resolve_hamiltonian(context, hop)
    if isinstance(op_ast, GridHamiltonianRef):
        gh = context.grid_hamiltonians[op_ast.alias]
        return context._evolve_precomputed_grid(joint, names, gh, duration)
    assert nq is not None

    non_qubit_result = _evolve_non_qubit_basis(
        context, joint, names, op_ast, nq, duration
    )
    if non_qubit_result is not None:
        return non_qubit_result

    # ADR 0205 / LISS-0404: a single tuple-valued coordinate (e.g. from
    # prepare_selection) stands in for nq separate qubit wires -- same
    # Hamiltonian, same compile_sparse_pauli/expm_ih_apply primitives,
    # verified by direct execution to give physically identical
    # results to the nq-separate-names path below (ADR 0205 Context).
    if len(names) == 1:
        src = names[0]
        sample = next(
            (w.assign.get(src) for w in joint.worlds if src in w.assign), None
        )
        if isinstance(sample, tuple):
            if len(sample) != nq:
                raise KernelError(
                    f"Operator needs {nq} qubit positions, tuple coordinate "
                    f"`{src}` has {len(sample)}"
                )
            from ..sparse_pauli import compile_sparse_pauli

            try:
                terms = compile_sparse_pauli(
                    op_ast,
                    env=context.operators,
                    scalars=context.scalars,
                    n_qubits=nq,
                )
            except ValueError as e:
                raise KernelError(str(e)) from e
            return context._hamiltonian_evolve_tuple_coordinate(
                joint, src, nq, terms, duration
            )

    # Multi-qubit Pauli H on names[0..nq) — sparse Pauli-sum + Taylor e^{-iHt}
    if len(names) < nq:
        raise KernelError(
            f"Operator needs {nq} qubit wires, bind has {len(names)}"
        )
    wires = names[:nq]
    from ..sparse_pauli import compile_sparse_pauli, expm_ih_apply

    try:
        terms = compile_sparse_pauli(
            op_ast,
            env=context.operators,
            scalars=context.scalars,
            n_qubits=nq,
        )
    except ValueError as e:
        raise KernelError(str(e)) from e

    dim = 2**nq
    # Build amplitude vector over computational basis; other coords kept per world
    # Strategy: group worlds by non-wire assigns; within each group apply U on wire bits
    from collections import defaultdict

    groups: dict[tuple, list[World]] = defaultdict(list)
    for w in joint.worlds:
        key = tuple(sorted((k, v) for k, v in w.assign.items() if k not in wires))
        groups[key].append(w)

    out_worlds: list[World] = []
    for key, ws in groups.items():
        vec = [0j] * dim
        phases = {}
        for w in ws:
            bits = []
            ok = True
            for name in wires:
                if name not in w.assign or w.assign[name] not in (0, 1):
                    ok = False
                    break
                bits.append(int(w.assign[name]))
            if not ok:
                raise KernelError(
                    f"hamiltonian evolve expects qubit bits on {wires}"
                )
            idx = 0
            for b in bits:
                idx = (idx << 1) | b
            vec[idx] += w.amp
            phases[idx] = dict(w.coord_phase)
        try:
            outv = expm_ih_apply(terms, duration, vec)
        except ValueError as e:
            raise KernelError(str(e)) from e
        base_assign = dict(key)
        for idx, amp in enumerate(outv):
            if abs(amp) ** 2 <= EPS:
                continue
            assign = dict(base_assign)
            # unpack bits MSB = wires[0]
            x = idx
            bit_list = []
            for _ in range(nq):
                bit_list.append(x & 1)
                x >>= 1
            bit_list.reverse()
            for name, bit in zip(wires, bit_list):
                assign[name] = bit
            out_worlds.append(
                World(
                    assign=assign,
                    amp=amp,
                    coord_phase=phases.get(idx, {}),
                )
            )
    return Joint(worlds=_coalesce(out_worlds))

def hamiltonian_evolve_tuple_coordinate(
    context: EvaluatorContext,
    joint: Joint,
    src: str,
    nq: int,
    terms: Any,
    t: float,
) -> Joint:
    """ADR 0205 / LISS-0404: same Pauli-sum evolution as the
    nq-separate-names path above, reading/writing one tuple-valued
    coordinate's `nq` positions instead of `nq` separate coordinate
    names. Verified by direct execution to give physically identical
    results to that path (ADR 0205 Context point 3).
    """
    from collections import defaultdict

    from ..joint import World, _coalesce
    from ..sparse_pauli import expm_ih_apply

    dim = 2**nq
    groups: dict[tuple, list[World]] = defaultdict(list)
    for w in joint.worlds:
        key = tuple(sorted((k, v) for k, v in w.assign.items() if k != src))
        groups[key].append(w)

    out_worlds: list[World] = []
    for key, ws in groups.items():
        vec = [0j] * dim
        phases: dict[int, dict[str, complex]] = {}
        for w in ws:
            pattern = w.assign[src]
            idx = 0
            for b in pattern:
                idx = (idx << 1) | int(b)
            vec[idx] += w.amp
            phases[idx] = dict(w.coord_phase)
        outv = expm_ih_apply(terms, t, vec)
        base_assign = dict(key)
        for idx, amp in enumerate(outv):
            if abs(amp) ** 2 <= EPS:
                continue
            x = idx
            bits = []
            for _ in range(nq):
                bits.append(x & 1)
                x >>= 1
            bits.reverse()
            assign = dict(base_assign)
            assign[src] = tuple(bits)
            out_worlds.append(
                World(assign=assign, amp=amp, coord_phase=phases.get(idx, {}))
            )
    return Joint(worlds=_coalesce(out_worlds))

def evolve_precomputed_grid(
    context: EvaluatorContext,
    joint: Joint,
    names: list[str],
    grid: GridHamiltonian,
    t: float,
) -> Joint:
    from ..joint import World, _coalesce
    from ..matrix import apply_mat, expm_ih

    if len(names) != 1:
        raise KernelError("grid Hamiltonian evolve requires a single bind name")
    src = names[0]
    amps = joint.amplitude_marginal(src)
    keys = sorted(amps.keys(), key=lambda x: float(x))
    if not keys or any(not isinstance(k, (int, float)) for k in keys):
        raise KernelError("grid evolve expects Float (or Int) abscissae")
    xs = list(grid.xs)
    if len(keys) != len(xs) or any(abs(float(k) - x) > 1e-9 for k, x in zip(keys, xs)):
        raise KernelError(
            "grid state abscissae must match the lowered discretization grid"
        )
    hmat = [list(row) for row in grid.matrix]
    u = expm_ih(hmat, t)
    vec = [amps[k] for k in keys]
    outv = apply_mat(u, vec)
    out_w = [
        World(assign={src: keys[i]}, amp=outv[i])
        for i in range(len(keys))
        if abs(outv[i]) ** 2 > EPS
    ]
    return Joint(worlds=_coalesce(out_w))
