"""General Operator projection over finite-support runtime states."""

from __future__ import annotations

import cmath
from collections.abc import Mapping, MutableMapping
from typing import Any, Protocol

from .errors import KernelError
from ..hamiltonian import compile_hamiltonian
from ..joint import EPS, Joint, World, _coalesce


class OperatorProjectionContext(Protocol):
    """Narrow view of evaluator-owned state needed by Operator projection."""

    operators: Mapping[str, Any]
    _compiled_operator_cache: MutableMapping[tuple[str, int], Any]


def project_onto_operator(
    context: OperatorProjectionContext,
    joint: Joint,
    coord_name: str,
    operator_name: str,
) -> Joint:
    """Apply the existing diagonal general-Operator projection semantics.

    Operator bindings and the compiled matrix cache remain owned by the live
    Evaluator context. Projection scales amplitudes without renormalizing.
    """
    op_ast = context.operators.get(operator_name)
    if op_ast is None:
        raise KernelError(f"project onto `{operator_name}`: unknown Operator")

    sample = next(
        (
            world.assign.get(coord_name)
            for world in joint.worlds
            if isinstance(world.assign.get(coord_name), tuple)
        ),
        None,
    )
    if sample is None:
        raise KernelError(
            "project onto a general Operator requires a tuple-valued "
            "coordinate"
        )

    width = len(sample)
    cache_key = (operator_name, width)
    matrix = context._compiled_operator_cache.get(cache_key)
    if matrix is None:
        matrix = compile_hamiltonian(op_ast, env={}, n_qubits=width)
        context._compiled_operator_cache[cache_key] = matrix

    dimension = len(matrix)
    for row in range(dimension):
        for column in range(dimension):
            if row != column and abs(matrix[row][column]) > EPS:
                raise KernelError(
                    "project onto a general Operator currently supports "
                    "diagonal projectors only (e.g. Sigma (x In F) "
                    "{ |x><x| }); the given Operator has a non-zero "
                    "off-diagonal entry"
                )

    out: list[World] = []
    for world in joint.worlds:
        pattern = world.assign.get(coord_name)
        if not isinstance(pattern, tuple):
            continue

        index = 0
        for bit in pattern:
            index = index * 2 + int(bit)
        diagonal = matrix[index][index].real
        if diagonal <= EPS:
            continue

        amplitude = world.amp * cmath.sqrt(diagonal)
        if abs(amplitude) ** 2 <= EPS:
            continue
        out.append(
            World(
                assign=dict(world.assign),
                amp=amplitude,
                coord_phase=dict(world.coord_phase),
            )
        )

    if not out:
        return Joint.empty()
    return Joint(worlds=_coalesce(out))
