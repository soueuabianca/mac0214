"""Utilidades compartilhadas pela visualização de árvores (BST e AVL).

O modelo interno é um nó mutável simples (`Node`); a saída para o front-end é
o schema aninhado `TreeNode`. Cada passo (`Step`) carrega a árvore inteira com
um estado de realce por nó, além de linha de código e descrição didática.
"""
from collections import deque
from typing import Dict, List, Optional

from schemas import Step, TreeNode


class Node:
    __slots__ = ("value", "left", "right", "height")

    def __init__(self, value: int):
        self.value = value
        self.left: Optional["Node"] = None
        self.right: Optional["Node"] = None
        self.height = 1


def h(n: Optional[Node]) -> int:
    return n.height if n else 0


def update(n: Node) -> None:
    n.height = 1 + max(h(n.left), h(n.right))


def balance(n: Optional[Node]) -> int:
    return h(n.left) - h(n.right) if n else 0


def from_schema(t: Optional[TreeNode]) -> Optional[Node]:
    """Reconstrói a árvore interna a partir do schema reenviado pelo front."""
    if t is None:
        return None
    n = Node(t.value)
    n.left = from_schema(t.left)
    n.right = from_schema(t.right)
    update(n)
    return n


def snapshot(
    n: Optional[Node], states: Optional[Dict[int, str]] = None, avl: bool = False
) -> Optional[TreeNode]:
    if n is None:
        return None
    states = states or {}
    return TreeNode(
        value=n.value,
        left=snapshot(n.left, states, avl),
        right=snapshot(n.right, states, avl),
        state=states.get(n.value, "normal"),
        height=n.height if avl else None,
        balance=balance(n) if avl else None,
    )


def mk(root, code_line, description, states=None, avl=False) -> Step:
    """Monta um Step com a fotografia atual da árvore."""
    return Step(
        array_snapshot=[],
        code_line=code_line,
        description=description,
        tree=snapshot(root, states, avl),
    )


# ---------------------------------------------------------------- rotações
def rot_left(x: Node) -> Node:
    y = x.right
    x.right = y.left
    y.left = x
    update(x)
    update(y)
    return y


def rot_right(y: Node) -> Node:
    x = y.left
    y.left = x.right
    x.right = y
    update(y)
    update(x)
    return x


def rebalance(n: Node):
    """Rebalanceia `n`. Retorna (nova_subraiz, descrição_do_caso).

    Usa os fatores de balanceamento dos filhos, então serve para inserção e
    remoção. Se já estiver equilibrado, devolve (n, None).
    """
    bf = balance(n)
    if bf > 1:
        if balance(n.left) < 0:
            n.left = rot_left(n.left)
            return rot_right(n), "Esquerda-Direita (LR)"
        return rot_right(n), "Direita (LL)"
    if bf < -1:
        if balance(n.right) > 0:
            n.right = rot_right(n.right)
            return rot_left(n), "Direita-Esquerda (RL)"
        return rot_left(n), "Esquerda (RR)"
    return n, None


# ------------------------------------------------ busca e travessias comuns
def search_steps(root, key, steps, *, avl=False, cmp_line, found_line, miss_line):
    cur = root
    while cur:
        steps.append(
            mk(root, cmp_line, f"search({key}): comparando com {cur.value}.", {cur.value: "compared"}, avl)
        )
        if key == cur.value:
            steps.append(mk(root, found_line, f"Valor {key} encontrado!", {cur.value: "found"}, avl))
            return
        cur = cur.left if key < cur.value else cur.right
    steps.append(mk(root, miss_line, f"Valor {key} não está na árvore.", {}, avl))


def traverse_steps(root, mode, steps, *, avl=False):
    order: List[int] = []

    def visit(n: Node):
        order.append(n.value)
        st = {v: "visited" for v in order}
        st[n.value] = "active"
        steps.append(
            mk(root, None, f"{mode}: visita {n.value}. Ordem até agora: {', '.join(map(str, order))}.", st, avl)
        )

    def rec(n):
        if not n:
            return
        if mode == "preorder":
            visit(n)
            rec(n.left)
            rec(n.right)
        elif mode == "postorder":
            rec(n.left)
            rec(n.right)
            visit(n)
        else:  # inorder
            rec(n.left)
            visit(n)
            rec(n.right)

    if root is None:
        steps.append(mk(None, None, "Árvore vazia: nada a percorrer.", {}, avl))
        return

    if mode == "level":
        q = deque([root])
        while q:
            n = q.popleft()
            visit(n)
            if n.left:
                q.append(n.left)
            if n.right:
                q.append(n.right)
    else:
        rec(root)

    st = {v: "visited" for v in order}
    steps.append(mk(root, None, f"Travessia {mode} concluída: {', '.join(map(str, order))}.", st, avl))
