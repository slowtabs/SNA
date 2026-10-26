"""Regression checks for the reusable from-scratch centrality implementations."""

import networkx as nx
import pytest

from src.centrality_algorithms import (
    bfs_distances,
    compute_centralities,
    manual_betweenness_centrality,
    manual_closeness_centrality,
    manual_degree_centrality,
    manual_eigenvector_centrality,
    manual_pagerank,
)


def assert_score_dicts_close(actual, expected, tolerance=1e-6):
    assert actual.keys() == expected.keys()
    for node in expected:
        assert actual[node] == pytest.approx(expected[node], abs=tolerance)


def test_bfs_returns_unweighted_shortest_path_distances():
    graph = nx.path_graph(5)
    assert bfs_distances(graph, 2) == {0: 2, 1: 1, 2: 0, 3: 1, 4: 2}


def test_manual_metrics_match_networkx_on_karate_club():
    graph = nx.karate_club_graph()

    assert_score_dicts_close(manual_degree_centrality(graph), nx.degree_centrality(graph))
    assert_score_dicts_close(manual_closeness_centrality(graph), nx.closeness_centrality(graph))
    assert_score_dicts_close(
        manual_betweenness_centrality(graph),
        nx.betweenness_centrality(graph),
    )
    assert_score_dicts_close(
        manual_eigenvector_centrality(graph),
        nx.eigenvector_centrality(graph, max_iter=5_000),
        tolerance=1e-5,
    )
    assert_score_dicts_close(
        manual_pagerank(graph),
        nx.pagerank(graph, weight=None),
        tolerance=1e-5,
    )


def test_compute_centralities_exposes_all_project_metrics():
    scores = compute_centralities(nx.path_graph(4))
    assert set(scores) == {"degree", "closeness", "betweenness", "eigenvector", "pagerank"}
    assert all(set(metric_scores) == {0, 1, 2, 3} for metric_scores in scores.values())
