"""Árvore Binária de Busca (BST) — geração de passos para visualização.

Operações: insert, search, delete (remoção de Hibbard) e traverse
(inorder | preorder | postorder | level). As linhas de código (`code_line`)
referenciam o array `code` de `data/trees.json` sob a chave "bst".
"""
from typing import List, Optional

from schemas import Step
from trees.common import Node, from_schema, mk, search_steps, traverse_steps

_TRAVERSALS = {"inorder", "preorder", "postorder", "level"}
_VALUE_VERBS = {"insert", "search", "delete"}


def _parse(op: str):
    parts = op.replace(",", " ").split()
    if not parts:
        raise ValueError("Operação vazia.")
    verb = parts[0].lower()
    if verb == "traverse":
        mode = parts[1].lower() if len(parts) > 1 else "inorder"
        if mode not in _TRAVERSALS:
            raise ValueError(
                f"Travessia '{mode}' inválida. Use: {', '.join(sorted(_TRAVERSALS))}."
            )
        return verb, mode
    if verb not in _VALUE_VERBS:
        raise ValueError(
            f"Operação '{verb}' inválida. Use: insert <n>, search <n>, "
            "delete <n>, traverse <ordem>."
        )
    if len(parts) < 2:
        raise ValueError(f"'{verb}' exige um valor inteiro. Ex.: {verb} 5.")
    try:
        return verb, int(parts[1])
    except ValueError:
        raise ValueError(f"Argumento inválido em '{op}'.")


def _insert(root, key, steps):
    if root is None:
        n = Node(key)
        steps.append(mk(n, 3, f"Árvore vazia: {key} torna-se a raiz.", {key: "inserted"}))
        return n
    cur = root
    while True:
        steps.append(mk(root, 4, f"insert({key}): comparando com {cur.value}.", {cur.value: "compared"}))
        if key == cur.value:
            steps.append(mk(root, 8, f"{key} já existe. A BST não armazena duplicatas.", {cur.value: "found"}))
            return root
        if key < cur.value:
            if cur.left is None:
                cur.left = Node(key)
                steps.append(mk(root, 5, f"{key} < {cur.value}: novo nó à esquerda.", {key: "inserted"}))
                return root
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = Node(key)
                steps.append(mk(root, 7, f"{key} > {cur.value}: novo nó à direita.", {key: "inserted"}))
                return root
            cur = cur.right


def _delete(root, key, steps):
    parent, cur = None, root
    while cur and cur.value != key:
        steps.append(mk(root, 17, f"delete({key}): comparando com {cur.value}.", {cur.value: "compared"}))
        parent, cur = cur, (cur.left if key < cur.value else cur.right)

    if cur is None:
        steps.append(mk(root, 16, f"{key} não está na árvore, nada a remover.", {}))
        return root
    steps.append(mk(root, 19, f"{key} encontrado (destacado para remoção).", {cur.value: "removed"}))

    # Dois filhos: substitui pelo sucessor in-order (mínimo da subárvore direita).
    if cur.left and cur.right:
        sp, succ = cur, cur.right
        while succ.left:
            steps.append(
                mk(root, 22, f"Sucessor in-order: desce à esquerda de {succ.value}.",
                   {cur.value: "removed", succ.value: "compared"})
            )
            sp, succ = succ, succ.left
        steps.append(
            mk(root, 23, f"Sucessor in-order = {succ.value}. Copia o valor para o nó removido.",
               {cur.value: "removed", succ.value: "active"})
        )
        cur.value = succ.value
        if sp.left is succ:
            sp.left = succ.right
        else:
            sp.right = succ.right
        steps.append(mk(root, 24, "Sucessor duplicado removido.", {cur.value: "active"}))
        return root

    # Zero ou um filho: liga o pai diretamente ao (único) filho.
    child = cur.left or cur.right
    if parent is None:
        root = child
    elif parent.left is cur:
        parent.left = child
    else:
        parent.right = child
    steps.append(mk(root, 20, f"Nó {key} removido.", {}))
    return root


def generate_bst_steps(operations: List[str], initial=None) -> List[Step]:
    root = from_schema(initial)
    steps: List[Step] = []
    steps.append(mk(root, None, "Estado atual da árvore." if root else "Árvore binária de busca vazia."))

    for op in operations:
        verb, arg = _parse(op)
        if verb == "insert":
            root = _insert(root, arg, steps)
        elif verb == "search":
            search_steps(root, arg, steps, cmp_line=11, found_line=11, miss_line=13)
        elif verb == "delete":
            root = _delete(root, arg, steps)
        elif verb == "traverse":
            traverse_steps(root, arg, steps)

    steps.append(mk(root, None, "Operação concluída."))
    return steps
