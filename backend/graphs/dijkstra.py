"""Dijkstra — caminhos mínimos em grafo ponderado (pesos não negativos).

Fila de prioridade + relaxamento de arestas. Rótulo = distância acumulada.
Linhas de código (`code_line`) referenciam `data/graphs.json` sob "dijkstra".
"""
import heapq
from typing import List

from graphs.common import Graph, mark_path, mk
from schemas import GraphInput, Step

_INF = float("inf")


def generate_dijkstra_steps(payload: GraphInput) -> List[Step]:
    g = Graph(payload.graph)
    source, target = payload.source, payload.target
    if source not in g.nodes:
        raise ValueError(f"Vértice de origem {source} não existe no grafo.")

    steps: List[Step] = []
    dist = {nid: _INF for nid in g.order}
    dist[source] = 0
    node_state = {source: "source"}
    edge_state = {}
    tree_edges = set()
    parent_edge, parent_node = {}, {}
    settled = set()

    def shown():
        return {k: (None if v == _INF else v) for k, v in dist.items()}

    def d(v):
        return "∞" if dist[v] == _INF else dist[v]

    steps.append(mk(g, 2, f"Dijkstra de {source}. dist[{source}] = 0, demais = ∞.",
                    dict(node_state), shown(), dict(edge_state)))

    pq = [(0, source)]
    while pq:
        du, u = heapq.heappop(pq)
        if u in settled:
            continue
        settled.add(u)
        node_state[u] = "current"
        steps.append(mk(g, 5, f"Fixa {u} com dist = {du} (menor da fila).",
                        dict(node_state), shown(), dict(edge_state)))

        for (w, weight, ei) in g.neighbors(u):
            wt = 1 if weight is None else weight
            edge_state[ei] = "considered"
            nd = dist[u] + wt
            steps.append(mk(g, 8, f"Relaxa {u}→{w} (peso {wt}): {dist[u]} + {wt} = {nd} vs dist[{w}] = {d(w)}.",
                            dict(node_state), shown(), dict(edge_state)))
            if nd < dist[w]:
                dist[w] = nd
                if w in parent_edge:
                    old = parent_edge[w]
                    tree_edges.discard(old)
                    edge_state[old] = "normal"
                parent_edge[w], parent_node[w] = ei, u
                tree_edges.add(ei)
                edge_state[ei] = "tree"
                if w not in settled:
                    node_state[w] = "frontier"
                heapq.heappush(pq, (nd, w))
                steps.append(mk(g, 9, f"Melhora dist[{w}] = {nd}. Aresta {u}–{w} entra na árvore de caminhos.",
                                dict(node_state), shown(), dict(edge_state)))
            else:
                edge_state[ei] = "tree" if ei in tree_edges else "normal"

        node_state[u] = "visited"

    if target is not None and dist.get(target, _INF) < _INF:
        mark_path(g, parent_edge, parent_node, target, source, node_state, edge_state)

    resumo = ", ".join(f"{k}:{d(k)}" for k in g.order)
    steps.append(mk(g, None, f"Dijkstra concluído. Distâncias mínimas — {resumo}.",
                    dict(node_state), shown(), dict(edge_state)))
    return steps
