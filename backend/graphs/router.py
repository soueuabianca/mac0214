import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from graphs.bfs import generate_bfs_steps
from graphs.dfs import generate_dfs_steps
from graphs.dijkstra import generate_dijkstra_steps
from schemas import AlgorithmResponse, GraphInput, MetadataResponse

# O prefixo "/api/v1/graphs" é aplicado por main.py via include_router.
router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "graphs.json"

ALGORITHMS = {
    "bfs": ("Busca em Largura (BFS)", generate_bfs_steps),
    "dfs": ("Busca em Profundidade (DFS)", generate_dfs_steps),
    "dijkstra": ("Dijkstra", generate_dijkstra_steps),
}

MAX_NODES = 60


@router.get("/algorithms")
def list_algorithms():
    """Lista os algoritmos de grafo disponíveis (usado pelo menu/busca)."""
    return [{"key": key, "name": name} for key, (name, _) in ALGORITHMS.items()]


@router.post("/{algo}", response_model=AlgorithmResponse)
def run_graph(algo: str, payload: GraphInput):
    """Executa um algoritmo de grafo e devolve os snapshots."""
    if algo not in ALGORITHMS:
        raise HTTPException(status_code=404, detail=f"Algoritmo de grafo '{algo}' não existe.")
    if not payload.graph.nodes:
        raise HTTPException(status_code=400, detail="O grafo está vazio.")
    if len(payload.graph.nodes) > MAX_NODES:
        raise HTTPException(status_code=400, detail=f"Limite de {MAX_NODES} vértices excedido.")

    name, generator = ALGORITHMS[algo]
    try:
        steps = generator(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return AlgorithmResponse(algorithm=name, steps=steps)


@router.get("/{algo}/metadata", response_model=MetadataResponse)
def get_algorithm_metadata(algo: str):
    """Devolve teoria, código-fonte e quiz de um algoritmo de grafo."""
    if not DATA_PATH.exists():
        raise HTTPException(status_code=500, detail="Base de metadados não encontrada no servidor.")

    with open(DATA_PATH, "r", encoding="utf-8") as file:
        try:
            metadata_db = json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Erro de formatação no arquivo JSON de metadados.")

    if algo not in metadata_db:
        raise HTTPException(status_code=404, detail=f"Metadados para '{algo}' não encontrados.")

    return metadata_db[algo]
