"""Provider-neutral R01 discrete interaction projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class InteractionEdge:
    edge_id: str
    left: str
    right: str
    weight: float


@dataclass(frozen=True)
class InteractionGraph:
    graph_id: str
    nodes: tuple[str, ...]
    edges: tuple[InteractionEdge, ...]
    source_hash: str


@dataclass(frozen=True)
class InteractionLaw:
    law_id: str
    local_fields: Mapping[str, float]
    weight_unit: str
    symmetry: str


@dataclass(frozen=True)
class IsingProjection:
    kind: str
    graph_id: str
    law_id: str
    variable_index: Mapping[str, int]
    interactions: tuple[tuple[int, int, float], ...]
    local_fields: tuple[float, ...]
    offset: float
    scale: float
    source_hash: str

    def energy(self, spins: tuple[int, ...]) -> float:
        if len(spins) != len(self.variable_index):
            raise DiscreteProfileError(
                "DISCRETE_INDEX_MISMATCH",
                "spin assignment does not match index",
            )
        return self.offset + self.scale * (
            sum(
                weight * spins[left] * spins[right]
                for left, right, weight in self.interactions
            )
            + sum(
                field * spins[index]
                for index, field in enumerate(self.local_fields)
            )
        )

    def decode(self, spins: tuple[int, ...]) -> dict[str, int]:
        if len(spins) != len(self.variable_index):
            raise DiscreteProfileError(
                "DISCRETE_INDEX_MISMATCH",
                "spin assignment does not match index",
            )
        return {
            variable: spins[index]
            for variable, index in self.variable_index.items()
        }


class DiscreteProfileError(ValueError):
    """Raised when an R01 graph cannot be projected safely."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


_SUPPORTED_TARGET = "finite-binary-projection"


def _validate_target(target: str) -> None:
    if target != _SUPPORTED_TARGET:
        raise DiscreteProfileError(
            "DISCRETE_UNSUPPORTED_TARGET",
            f"unsupported target: {target}",
        )


def _require_law(law: InteractionLaw | None) -> InteractionLaw:
    if law is None:
        raise DiscreteProfileError(
            "DISCRETE_GRAPH_AS_HAMILTONIAN",
            "graph is not a Hamiltonian without an explicit interaction law"
        )
    return law


def _variable_index(graph: InteractionGraph) -> dict[str, int]:
    if len(set(graph.nodes)) != len(graph.nodes):
        raise DiscreteProfileError(
            "DISCRETE_INDEX_MISMATCH",
            "index mismatch: graph nodes are not unique",
        )
    return {node: index for index, node in enumerate(graph.nodes)}


def _validate_edges(
    graph: InteractionGraph,
    variable_index: Mapping[str, int],
) -> None:
    node_set = set(graph.nodes)
    seen_edges: set[tuple[str, str]] = set()
    for edge in graph.edges:
        if edge.left not in node_set or edge.right not in node_set:
            raise DiscreteProfileError(
                "DISCRETE_INDEX_MISMATCH",
                "index mismatch: edge endpoint is not a graph node",
            )
        key = tuple(sorted((edge.left, edge.right)))
        if key in seen_edges:
            raise DiscreteProfileError(
                "DISCRETE_DUPLICATE_EDGE",
                "duplicate edge in interaction graph",
            )
        seen_edges.add(key)
    if set(variable_index) != node_set:
        raise DiscreteProfileError(
            "DISCRETE_INDEX_MISMATCH",
            "index mismatch: graph index does not cover nodes",
        )


def _validate_law(graph: InteractionGraph, law: InteractionLaw) -> None:
    if set(law.local_fields) != set(graph.nodes):
        raise DiscreteProfileError(
            "DISCRETE_INDEX_MISMATCH",
            "index mismatch: local fields do not cover graph nodes",
        )
    if law.symmetry != "undirected":
        raise DiscreteProfileError(
            "DISCRETE_SYMMETRY_MISMATCH",
            "symmetry mismatch: R01 requires undirected interactions",
        )


def _build_interactions(
    graph: InteractionGraph,
    variable_index: Mapping[str, int],
) -> tuple[tuple[int, int, float], ...]:
    return tuple(
        (variable_index[edge.left], variable_index[edge.right], float(edge.weight))
        for edge in graph.edges
    )


def _build_local_fields(
    graph: InteractionGraph,
    law: InteractionLaw,
) -> tuple[float, ...]:
    return tuple(float(law.local_fields[node]) for node in graph.nodes)


def project_interaction(
    *,
    graph: InteractionGraph,
    law: InteractionLaw | None,
    target: str,
) -> IsingProjection:
    """Build an explicit finite Ising projection from a graph and law."""

    _validate_target(target)
    resolved_law = _require_law(law)
    variable_index = _variable_index(graph)
    _validate_edges(graph, variable_index)
    _validate_law(graph, resolved_law)
    return IsingProjection(
        kind="ising-hamiltonian",
        graph_id=graph.graph_id,
        law_id=resolved_law.law_id,
        variable_index=variable_index,
        interactions=_build_interactions(graph, variable_index),
        local_fields=_build_local_fields(graph, resolved_law),
        offset=0.0,
        scale=1.0,
        source_hash=graph.source_hash,
    )
