"""Árvore AVL — BST auto-balanceada por altura, com rotações animadas.

insert/delete atualizam alturas ao longo do caminho e disparam rotações
(LL, RR, LR, RL) quando o fator de balanceamento sai de [-1, 1]. search e
traverse são compartilhados com a BST (trees.common). As linhas de código
(`code_line`) referenciam o array `code` de `data/trees.json` sob "avl".
"""
from typing import List

from schemas import Step
from trees.common import (
    Node,
    balance,
    from_schema,
    mk,
    rebalance,
    search_steps,
    traverse_steps,
    update,
)

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


def _fixup(root, path, steps):
    """Sobe o caminho de inserção/remoção, atualiza alturas e rotaciona."""
    for i in range(len(path) - 1, -1, -1):
        n = path[i]
        update(n)
        bf = balance(n)
        if -1 <= bf <= 1:
            continue
        parent = path[i - 1] if i > 0 else None
        newsub, kind = rebalance(n)
        if parent is None:
            root = newsub
        elif parent.left is n:
            parent.left = newsub
        else:
            parent.right = newsub
        steps.append(
            mk(root, 8, f"Nó {n.value} desbalanceado (fb={bf}). Rotação {kind}.",
               {newsub.value: "active"}, avl=True)
        )
    return root


def _insert(root, key, steps):
    if root is None:
        n = Node(key)
        steps.append(mk(n, 2, f"Árvore vazia: {key} é a raiz.", {key: "inserted"}, avl=True))
        return n

    path = []
    cur = root
    while True:
        steps.append(mk(root, 3, f"insert({key}): comparando com {cur.value}.", {cur.value: "compared"}, avl=True))
        path.append(cur)
        if key == cur.value:
            steps.append(mk(root, 8, f"{key} já existe.", {cur.value: "found"}, avl=True))
            return root
        if key < cur.value:
            if cur.left is None:
                cur.left = Node(key)
                break
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = Node(key)
                break
            cur = cur.right

    steps.append(mk(root, 4, f"{key} inserido como folha.", {key: "inserted"}, avl=True))
    return _fixup(root, path, steps)


def _delete(root, key, steps):
    if root is None:
        steps.append(mk(None, None, "Árvore vazia, nada a remover.", {}, avl=True))
        return None

    path = []
    parent, cur = None, root
    while cur and cur.value != key:
        steps.append(mk(root, None, f"delete({key}): comparando com {cur.value}.", {cur.value: "compared"}, avl=True))
        path.append(cur)
        parent, cur = cur, (cur.left if key < cur.value else cur.right)

    if cur is None:
        steps.append(mk(root, None, f"{key} não está na árvore.", {}, avl=True))
        return root
    steps.append(mk(root, None, f"{key} encontrado (destacado para remoção).", {cur.value: "removed"}, avl=True))

    if cur.left and cur.right:
        path.append(cur)
        sp, succ = cur, cur.right
        while succ.left:
            steps.append(
                mk(root, None, f"Sucessor in-order: desce à esquerda de {succ.value}.",
                   {cur.value: "removed", succ.value: "compared"}, avl=True)
            )
            path.append(succ)
            sp, succ = succ, succ.left
        steps.append(
            mk(root, None, f"Sucessor = {succ.value}. Copia o valor para o nó removido.",
               {cur.value: "removed", succ.value: "active"}, avl=True)
        )
        cur.value = succ.value
        if sp.left is succ:
            sp.left = succ.right
        else:
            sp.right = succ.right
    else:
        child = cur.left or cur.right
        if parent is None:
            root = child
        elif parent.left is cur:
            parent.left = child
        else:
            parent.right = child

    steps.append(mk(root, None, "Nó removido. Rebalanceando o caminho de volta à raiz…", {}, avl=True))
    return _fixup(root, path, steps)


def generate_avl_steps(operations: List[str], initial=None) -> List[Step]:
    root = from_schema(initial)
    steps: List[Step] = []
    steps.append(mk(root, None, "Estado atual da árvore AVL." if root else "Árvore AVL vazia.", {}, avl=True))

    for op in operations:
        verb, arg = _parse(op)
        if verb == "insert":
            root = _insert(root, arg, steps)
        elif verb == "search":
            search_steps(root, arg, steps, avl=True, cmp_line=None, found_line=None, miss_line=None)
        elif verb == "delete":
            root = _delete(root, arg, steps)
        elif verb == "traverse":
            traverse_steps(root, arg, steps, avl=True)

    steps.append(mk(root, None, "Operação concluída.", {}, avl=True))
    return steps
