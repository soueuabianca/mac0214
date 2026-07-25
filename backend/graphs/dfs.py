"""Busca em profundidade (DFS) recursiva. Rótulo = ordem de descoberta.

Linhas de código (`code_line`) referenciam `data/graphs.json` sob "dfs".
"""
from typing import List

from graphs.common import Graph, mark_path, mk
from schemas import GraphInput, Step


def generate_dfs_steps(payload: GraphInput) -> List[Step]:
    g = Graph(payload.graph)
    source, target = payload.source, payload.target
    if source not in g.nodes:
        raise ValueError(f"Vértice de origem {source} não existe no grafo.")

    steps: List[Step] = []
    node_state = {source: "source"}
    edge_state = {}
    tree_edges = set()
    dist = {}  # ordem de descoberta (pré-ordem)
    visited = set()
    parent_edge, parent_node = {}, {}
    counter = [0]

    def dfs(u):
        visited.add(u)
        node_state[u] = "current"
        dist[u] = counter[0]
        counter[0] += 1
        steps.append(mk(g, 2, f"Visita {u} (ordem de descoberta {dist[u]}).",
                        dict(node_state), dict(dist), dict(edge_state)))
        for (w, _weight, ei) in g.neighbors(u):
            edge_state[ei] = "considered"
            steps.append(mk(g, 3, f"Examina aresta {u}–{w}.",
                            dict(node_state), dict(dist), dict(edge_state)))
            if w in visited:
                edge_state[ei] = "tree" if ei in tree_edges else "normal"
                continue
            tree_edges.add(ei)
            edge_state[ei] = "tree"
            parent_edge[w], parent_node[w] = ei, u
            node_state[w] = "frontier"
            steps.append(mk(g, 5, f"{w} não visitado: desce recursivamente.",
                            dict(node_state), dict(dist), dict(edge_state)))
            dfs(w)
            node_state[u] = "current"
            steps.append(mk(g, 3, f"Retrocede para {u}.",
                            dict(node_state), dict(dist), dict(edge_state)))
        node_state[u] = "visited"

    dfs(source)

    if target is not None and target in visited:
        mark_path(g, parent_edge, parent_node, target, source, node_state, edge_state)

    resumo = ", ".join(str(k) for k, _ in sorted(dist.items(), key=lambda kv: kv[1]))
    steps.append(mk(g, None, f"DFS concluído. Ordem de visita: {resumo}.",
                    dict(node_state), dict(dist), dict(edge_state)))
    return steps
