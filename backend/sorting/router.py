import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from schemas import AlgorithmResponse, ArrayInput, MetadataResponse
from sorting.bubblesort import generate_bubble_sort_steps
from sorting.heapsort import generate_heap_sort_steps
from sorting.insertionsort import generate_insertion_sort_steps
from sorting.mergesort import generate_merge_sort_steps
from sorting.quicksort import generate_quick_sort_steps
from sorting.selectionsort import generate_selection_sort_steps

# O prefixo "/api/v1/sorting" é aplicado por main.py via include_router.
router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "sorting.json"

# Mapa único endpoint -> (nome amigável, gerador de passos).
ALGORITHMS = {
    "bubble": ("Bubble Sort", generate_bubble_sort_steps),
    "quick": ("Quick Sort", generate_quick_sort_steps),
    "merge": ("Merge Sort", generate_merge_sort_steps),
    "insertion": ("Insertion Sort", generate_insertion_sort_steps),
    "selection": ("Selection Sort", generate_selection_sort_steps),
    "heap": ("Heap Sort", generate_heap_sort_steps),
}

MAX_ELEMENTS = 30
MAX_VALUE = 999


@router.get("/algorithms")
def list_algorithms():
    """Lista os algoritmos de ordenação disponíveis (usado pelo menu/busca)."""
    return [{"key": key, "name": name} for key, (name, _) in ALGORITHMS.items()]


@router.post("/{algo_name}", response_model=AlgorithmResponse)
def run_sorting(algo_name: str, payload: ArrayInput):
    """Executa um algoritmo e devolve a sequência de snapshots."""
    if algo_name not in ALGORITHMS:
        raise HTTPException(
            status_code=404, detail=f"Algoritmo de ordenação '{algo_name}' não existe."
        )

    if not payload.data:
        raise HTTPException(status_code=400, detail="O array de entrada está vazio.")
    if len(payload.data) > MAX_ELEMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"Limite de {MAX_ELEMENTS} elementos excedido.",
        )
    if any(abs(v) > MAX_VALUE for v in payload.data):
        raise HTTPException(
            status_code=400,
            detail=f"Valores devem estar entre -{MAX_VALUE} e {MAX_VALUE}.",
        )

    name, generator = ALGORITHMS[algo_name]
    steps = generator(payload.data)
    return AlgorithmResponse(algorithm=name, steps=steps)


@router.get("/{algo_name}/metadata", response_model=MetadataResponse)
def get_algorithm_metadata(algo_name: str):
    """Devolve teoria, código-fonte e quiz de um algoritmo."""
    if not DATA_PATH.exists():
        raise HTTPException(
            status_code=500, detail="Base de metadados não encontrada no servidor."
        )

    with open(DATA_PATH, "r", encoding="utf-8") as file:
        try:
            metadata_db = json.load(file)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Erro de formatação no arquivo JSON de metadados.",
            )

    if algo_name not in metadata_db:
        raise HTTPException(
            status_code=404,
            detail=f"Metadados para o algoritmo '{algo_name}' não encontrados.",
        )

    return metadata_db[algo_name]
