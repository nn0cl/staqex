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
            raise DiscreteProfileError("spin assignment does not match index")
        return self.offset + self.scale * (
            sum(weight * spins[left] * spins[right] for left, right, weight in self.interactions)
            + sum(field * spins[index] for index, field in enumerate(self.local_fields))
        )

    def decode(self, spins: tuple[int, ...]) -> dict[str, int]:
        if len(spins) != len(self.variable_index):
            raise DiscreteProfileError("spin assignment does not match index")
        return {
            variable: spins[index]
            for variable, index in self.variable_index.items()
        }


class DiscreteProfileError(ValueError):
    """Raised when an R01 graph cannot be projected safely."""


_SUPPORTED_TARGET = "finite-binary-projection"


def _validate_graph(graph: InteractionGraph, law: InteractionLaw | None) -> None:
    if law is None:
        raise DiscreteProfileError(
            "graph is not a Hamiltonian without an explicit interaction law"
        )
    if len(set(graph.nodes)) != len(graph.nodes):
        raise DiscreteProfileError("index mismatch: graph nodes are not unique")
    node_set = set(graph.nodes)
    seen_edges: set[tuple[str, str]] = set()
    for edge in graph.edges:
        if edge.left not in node_set or edge.right not in node_set:
            raise DiscreteProfileError("index mismatch: edge endpoint is not a graph node")
        key = tuple(sorted((edge.left, edge.right)))
        if key in seen_edges:
            raise DiscreteProfileError("duplicate edge in interaction graph")
        seen_edges.add(key)


def _validate_law(graph: InteractionGraph, law: InteractionLaw) -> None:
    if set(law.local_fields) != set(graph.nodes):
        raise DiscreteProfileError("index mismatch: local fields do not cover graph nodes")
    if law.symmetry != "undirected":
        raise DiscreteProfileError("symmetry mismatch: R01 requires undirected interactions")


def project_interaction(
    *,
    graph: InteractionGraph,
    law: InteractionLaw | None,
    target: str,
) -> IsingProjection:
    """Build an explicit finite Ising projection from a graph and law."""

    if target != _SUPPORTED_TARGET:
        raise DiscreteProfileError(f"unsupported target: {target}")
    _validate_graph(graph, law)
    assert law is not None
    _validate_law(graph, law)

    variable_index = {node: index for index, node in enumerate(graph.nodes)}
    interactions = tuple(
        (variable_index[edge.left], variable_index[edge.right], float(edge.weight))
        for edge in graph.edges
    )
    local_fields = tuple(float(law.local_fields[node]) for node in graph.nodes)
    return IsingProjection(
        kind="ising-hamiltonian",
        graph_id=graph.graph_id,
        law_id=law.law_id,
        variable_index=variable_index,
        interactions=interactions,
        local_fields=local_fields,
        offset=0.0,
        scale=1.0,
        source_hash=graph.source_hash,
    )
