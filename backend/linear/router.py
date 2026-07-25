import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from linear.linkedlist import generate_linked_list_steps
from linear.queue import generate_queue_steps
from linear.stack import generate_stack_steps
from schemas import AlgorithmResponse, MetadataResponse, OperationInput

# O prefixo "/api/v1/linear" é aplicado por main.py via include_router.
router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "linear.json"

STRUCTURES = {
    "stack": ("Pilha (Stack)", generate_stack_steps),
    "queue": ("Fila (Queue)", generate_queue_steps),
    "linked": ("Lista Encadeada", generate_linked_list_steps),
}

MAX_OPERATIONS = 40
MAX_INITIAL = 60


@router.get("/algorithms")
def list_structures():
    """Lista as estruturas lineares disponíveis (usado pelo menu/busca)."""
    return [{"key": key, "name": name} for key, (name, _) in STRUCTURES.items()]


@router.post("/{struct}", response_model=AlgorithmResponse)
def run_structure(struct: str, payload: OperationInput):
    """Executa uma sequência de operações e devolve os snapshots."""
    if struct not in STRUCTURES:
        raise HTTPException(
            status_code=404, detail=f"Estrutura linear '{struct}' não existe."
        )
    if not payload.operations:
        raise HTTPException(status_code=400, detail="Nenhuma operação informada.")
    if len(payload.operations) > MAX_OPERATIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Limite de {MAX_OPERATIONS} operações excedido.",
        )
    if len(payload.initial) > MAX_INITIAL:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inicial excede o limite de {MAX_INITIAL} elementos.",
        )

    name, generator = STRUCTURES[struct]
    try:
        steps = generator(payload.operations, payload.initial)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return AlgorithmResponse(algorithm=name, steps=steps)


@router.get("/{struct}/metadata", response_model=MetadataResponse)
def get_structure_metadata(struct: str):
    """Devolve teoria, código-fonte e quiz de uma estrutura linear."""
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

    if struct not in metadata_db:
        raise HTTPException(
            status_code=404,
            detail=f"Metadados para a estrutura '{struct}' não encontrados.",
        )

    return metadata_db[struct]
