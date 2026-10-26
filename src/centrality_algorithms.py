"""Reusable centrality routines for the social-network analysis project.

The ``manual_*`` functions intentionally favour clarity over scale: they are
used to validate the library results on small, undirected, unweighted graphs.
For larger networks, use :func:`compute_centralities`, which delegates to
NetworkX's production implementations.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Hashable, Iterable, Mapping

import networkx as nx
import numpy as np


Node = Hashable
Scores = dict[Node, float]


def bfs_distances(adjacency: Mapping[Node, Iterable[Node]], source: Node) -> dict[Node, int]:
    """Return unweighted shortest-path distances from ``source`` using BFS."""
    distances: dict[Node, int] = {source: 0}
    queue: deque[Node] = deque([source])
    while queue:
        node = queue.popleft()
        for neighbour in adjacency[node]:
            if neighbour not in distances:
                distances[neighbour] = distances[node] + 1
                queue.append(neighbour)
    return distances


def compute_centralities(
    graph: nx.Graph,
    *,
    alpha: float = 0.85,
    max_iter: int = 1_000,
    tol: float = 1e-9,
) -> dict[str, Scores]:
    """Calculate the five centrality metrics used in this project with NetworkX.

    Edge weights are deliberately ignored so results describe the topology of
    the supplied social network.  The function works with directed graphs too;
    in that case NetworkX applies its directed definitions of the measures.
    """
    return {
        "degree": dict(nx.degree_centrality(graph)),
        "closeness": dict(nx.closeness_centrality(graph)),
        "betweenness": dict(
            nx.betweenness_centrality(graph, normalized=True, weight=None)
        ),
        "eigenvector": dict(
            nx.eigenvector_centrality(
                graph, max_iter=max_iter, tol=tol, weight=None
            )
        ),
        "pagerank": dict(
            nx.pagerank(
                graph, alpha=alpha, max_iter=max_iter, tol=tol, weight=None
            )
        ),
    }


def _require_undirected_simple(graph: nx.Graph) -> None:
    if graph.is_directed() or graph.is_multigraph():
        raise ValueError(
            "Manual validation routines support only simple, undirected graphs."
        )


def manual_degree_centrality(graph: nx.Graph) -> Scores:
    """Calculate normalized degree centrality without NetworkX centrality APIs."""
    _require_undirected_simple(graph)
    denominator = graph.number_of_nodes() - 1
    if denominator <= 0:
        return {node: 0.0 for node in graph}
    return {node: graph.degree(node) / denominator for node in graph}


def manual_closeness_centrality(graph: nx.Graph) -> Scores:
    """Calculate Wasserman--Faust normalized closeness using one BFS per node."""
    _require_undirected_simple(graph)
    node_count = graph.number_of_nodes()
    if node_count <= 1:
        return {node: 0.0 for node in graph}

    adjacency = {node: tuple(graph.neighbors(node)) for node in graph}
    scores: Scores = {}
    for node in graph:
        distances = bfs_distances(adjacency, node)
        reachable = len(distances) - 1
        distance_sum = sum(distances.values())
        if reachable == 0 or distance_sum == 0:
            scores[node] = 0.0
        else:
            scores[node] = (reachable / distance_sum) * (reachable / (node_count - 1))
    return scores


def manual_betweenness_centrality(graph: nx.Graph) -> Scores:
    """Calculate normalized betweenness centrality with Brandes' algorithm."""
    _require_undirected_simple(graph)
    nodes = list(graph)
    node_count = len(nodes)
    if node_count <= 2:
        return {node: 0.0 for node in nodes}

    adjacency = {node: tuple(graph.neighbors(node)) for node in nodes}
    betweenness: Scores = dict.fromkeys(nodes, 0.0)
    for source in nodes:
        stack: list[Node] = []
        predecessors: dict[Node, list[Node]] = {node: [] for node in nodes}
        path_count: Scores = dict.fromkeys(nodes, 0.0)
        distance: dict[Node, int] = dict.fromkeys(nodes, -1)
        path_count[source] = 1.0
        distance[source] = 0
        queue: deque[Node] = deque([source])

        while queue:
            vertex = queue.popleft()
            stack.append(vertex)
            for neighbour in adjacency[vertex]:
                if distance[neighbour] < 0:
                    distance[neighbour] = distance[vertex] + 1
                    queue.append(neighbour)
                if distance[neighbour] == distance[vertex] + 1:
                    path_count[neighbour] += path_count[vertex]
                    predecessors[neighbour].append(vertex)

        dependency: Scores = dict.fromkeys(nodes, 0.0)
        while stack:
            vertex = stack.pop()
            for predecessor in predecessors[vertex]:
                dependency[predecessor] += (
                    path_count[predecessor] / path_count[vertex]
                ) * (1.0 + dependency[vertex])
            if vertex != source:
                betweenness[vertex] += dependency[vertex]

    # Each unordered source-target pair was counted twice in an undirected graph.
    scale = 1.0 / ((node_count - 1) * (node_count - 2))
    return {node: score * scale for node, score in betweenness.items()}


def manual_eigenvector_centrality(
    graph: nx.Graph, *, max_iter: int = 1_000, tol: float = 1e-9
) -> Scores:
    """Calculate eigenvector centrality with power iteration on ``A + I``."""
    _require_undirected_simple(graph)
    nodes = list(graph)
    if not nodes:
        return {}
    adjacency = nx.to_numpy_array(graph, nodelist=nodes, weight=None, dtype=float)
    values = np.ones(len(nodes), dtype=float) / len(nodes)

    for _ in range(max_iter):
        updated = adjacency @ values + values  # A + I avoids bipartite oscillation.
        updated /= np.linalg.norm(updated)
        if np.linalg.norm(updated - values) < tol:
            return dict(zip(nodes, updated, strict=True))
        values = updated
    raise nx.PowerIterationFailedConvergence(max_iter)


def manual_pagerank(
    graph: nx.Graph, *, alpha: float = 0.85, max_iter: int = 1_000, tol: float = 1e-9
) -> Scores:
    """Calculate unweighted PageRank by power iteration, including dangling nodes."""
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between 0 and 1.")
    nodes = list(graph)
    node_count = len(nodes)
    if node_count == 0:
        return {}

    successors = {
        node: tuple(graph.successors(node) if graph.is_directed() else graph.neighbors(node))
        for node in nodes
    }
    rank: Scores = dict.fromkeys(nodes, 1.0 / node_count)
    for _ in range(max_iter):
        updated: Scores = dict.fromkeys(nodes, (1.0 - alpha) / node_count)
        dangling_rank = alpha * sum(rank[node] for node in nodes if not successors[node])
        for node in nodes:
            updated[node] += dangling_rank / node_count
            if successors[node]:
                share = alpha * rank[node] / len(successors[node])
                for neighbour in successors[node]:
                    updated[neighbour] += share
        error = sum(abs(updated[node] - rank[node]) for node in nodes)
        if error < node_count * tol:
            return updated
        rank = updated
    raise nx.PowerIterationFailedConvergence(max_iter)


def validate_manual_implementations(
    graph: nx.Graph, *, tolerance: float = 1e-5
) -> dict[str, dict[str, Any]]:
    """Compare manual results to NetworkX and return compact validation data."""
    _require_undirected_simple(graph)
    library = compute_centralities(graph)
    manual = {
        "degree": manual_degree_centrality(graph),
        "closeness": manual_closeness_centrality(graph),
        "betweenness": manual_betweenness_centrality(graph),
        "eigenvector": manual_eigenvector_centrality(graph),
        "pagerank": manual_pagerank(graph),
    }
    validation: dict[str, dict[str, Any]] = {}
    for metric, scores in manual.items():
        maximum_difference = max(
            (abs(scores[node] - library[metric][node]) for node in graph), default=0.0
        )
        validation[metric] = {
            "max_abs_difference": maximum_difference,
            "match": maximum_difference < tolerance,
        }
    return validation
