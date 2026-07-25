"""Busca em largura (BFS). Camadas a partir da origem; distâncias em arestas.

Linhas de código (`code_line`) referenciam `data/graphs.json` sob "bfs".
"""
from collections import deque
from typing import List, Optional

from graphs.common import Graph, mark_path, mk
from schemas import GraphInput, Step


def generate_bfs_steps(payload: GraphInput) -> List[Step]:
    g = Graph(payload.graph)
    source, target = payload.source, payload.target
    if source not in g.nodes:
        raise ValueError(f"Vértice de origem {source} não existe no grafo.")

    steps: List[Step] = []
    dist = {source: 0}
    node_state = {source: "source"}
    edge_state = {}
    tree_edges = set()
    parent_edge, parent_node = {}, {}
    q = deque([source])

    steps.append(mk(g, 2, f"BFS a partir de {source}. Fila = [{source}], dist[{source}] = 0.",
                    dict(node_state), dict(dist), dict(edge_state)))

    while q:
        u = q.popleft()
        node_state[u] = "current"
        steps.append(mk(g, 4, f"Retira {u} da fila e explora seus vizinhos.",
                        dict(node_state), dict(dist), dict(edge_state)))

        for (w, _weight, ei) in g.neighbors(u):
            edge_state[ei] = "considered"
            steps.append(mk(g, 5, f"Examina aresta {u}–{w}.",
                            dict(node_state), dict(dist), dict(edge_state)))
            if w in dist:
                edge_state[ei] = "tree" if ei in tree_edges else "normal"
                continue
            dist[w] = dist[u] + 1
            tree_edges.add(ei)
            edge_state[ei] = "tree"
            parent_edge[w], parent_node[w] = ei, u
            node_state[w] = "frontier"
            q.append(w)
            steps.append(mk(g, 8, f"Descobre {w} via {u}: dist[{w}] = {dist[w]}. Enfileira.",
                            dict(node_state), dict(dist), dict(edge_state)))

        node_state[u] = "visited"
        steps.append(mk(g, 4, f"Vértice {u} concluído.",
                        dict(node_state), dict(dist), dict(edge_state)))

    if target is not None and target in dist:
        mark_path(g, parent_edge, parent_node, target, source, node_state, edge_state)

    resumo = ", ".join(f"{k}:{v}" for k, v in sorted(dist.items()))
    steps.append(mk(g, None, f"BFS concluído. Distâncias em arestas — {resumo}.",
                    dict(node_state), dict(dist), dict(edge_state)))
    return steps
