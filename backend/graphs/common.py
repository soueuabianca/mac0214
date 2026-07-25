"""Utilidades compartilhadas pela visualização de grafos (BFS, DFS, Dijkstra).

O backend é agnóstico ao grafo: recebe nós (com posições x/y) e arestas do
front-end e devolve, a cada passo, uma fotografia do grafo com estados por nó
e por aresta, além de rótulos de distância. Grafos não-dirigidos; o peso é
ignorado por BFS/DFS e usado por Dijkstra.
"""
from typing import Dict, List, Optional, Tuple

from schemas import GraphEdge, GraphNode, GraphSnapshot, Step


class Graph:
    def __init__(self, snap: GraphSnapshot):
        self.directed = snap.directed
        self.nodes = {n.id: n for n in snap.nodes}   # preserva posições
        self.order = [n.id for n in snap.nodes]
        self.edges: List[Tuple[int, int, Optional[float]]] = [
            (e.u, e.v, e.weight) for e in snap.edges
        ]
        self.adj: Dict[int, List[Tuple[int, Optional[float], int]]] = {
            nid: [] for nid in self.order
        }
        for idx, e in enumerate(snap.edges):
            self.adj.setdefault(e.u, []).append((e.v, e.weight, idx))
            if not snap.directed:
                self.adj.setdefault(e.v, []).append((e.u, e.weight, idx))
        # Ordem determinística dos vizinhos (por id), no espírito do Sedgewick.
        for nid in self.adj:
            self.adj[nid].sort(key=lambda t: t[0])

    def neighbors(self, u):
        return self.adj.get(u, [])


def snapshot(g: Graph, nstate=None, ndist=None, estate=None) -> GraphSnapshot:
    nstate = nstate or {}
    ndist = ndist or {}
    estate = estate or {}
    nodes = [
        GraphNode(
            id=nid,
            x=g.nodes[nid].x,
            y=g.nodes[nid].y,
            state=nstate.get(nid, "normal"),
            dist=ndist.get(nid),
        )
        for nid in g.order
    ]
    edges = [
        GraphEdge(u=u, v=v, weight=w, state=estate.get(i, "normal"))
        for i, (u, v, w) in enumerate(g.edges)
    ]
    return GraphSnapshot(nodes=nodes, edges=edges, directed=g.directed)


def mk(g, code_line, description, nstate=None, ndist=None, estate=None) -> Step:
    return Step(
        array_snapshot=[],
        code_line=code_line,
        description=description,
        graph=snapshot(g, nstate, ndist, estate),
    )


def mark_path(g, parent_edge, parent_node, target, source, node_state, edge_state):
    """Realça o caminho de `source` a `target` seguindo os predecessores."""
    if target == source:
        node_state[source] = "source"
        return
    node_state[target] = "target"
    node = target
    guard = 0
    limit = len(g.order) + 1
    while node != source and node in parent_edge and guard < limit:
        edge_state[parent_edge[node]] = "inpath"
        node = parent_node[node]
        if node != source:
            node_state[node] = "inpath"
        guard += 1
    node_state[source] = "source"
