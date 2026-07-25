import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from schemas import AlgorithmResponse, MetadataResponse, TreeOperationInput
from trees.avl import generate_avl_steps
from trees.bst import generate_bst_steps

# O prefixo "/api/v1/trees" é aplicado por main.py via include_router.
router = APIRouter()

DATA_PATH = Path(__file__).parent.parent / "data" / "trees.json"

TREES = {
    "bst": ("Árvore Binária de Busca", generate_bst_steps),
    "avl": ("Árvore AVL", generate_avl_steps),
}

MAX_OPERATIONS = 40


@router.get("/algorithms")
def list_trees():
    """Lista as árvores disponíveis (usado pelo menu/busca)."""
    return [{"key": key, "name": name} for key, (name, _) in TREES.items()]


@router.post("/{tree}", response_model=AlgorithmResponse)
def run_tree(tree: str, payload: TreeOperationInput):
    """Executa operações e devolve os snapshots da árvore."""
    if tree not in TREES:
        raise HTTPException(status_code=404, detail=f"Árvore '{tree}' não existe.")
    if not payload.operations:
        raise HTTPException(status_code=400, detail="Nenhuma operação informada.")
    if len(payload.operations) > MAX_OPERATIONS:
        raise HTTPException(
            status_code=400, detail=f"Limite de {MAX_OPERATIONS} operações excedido."
        )

    name, generator = TREES[tree]
    try:
        steps = generator(payload.operations, payload.initial)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return AlgorithmResponse(algorithm=name, steps=steps)


@router.get("/{tree}/metadata", response_model=MetadataResponse)
def get_tree_metadata(tree: str):
    """Devolve teoria, código-fonte e quiz de uma árvore."""
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

    if tree not in metadata_db:
        raise HTTPException(
            status_code=404,
            detail=f"Metadados para a árvore '{tree}' não encontrados.",
        )

    return metadata_db[tree]
