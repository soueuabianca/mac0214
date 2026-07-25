from typing import List, Optional, Tuple

from schemas import Step

# Verbos aceitos e se exigem argumento inteiro.
_VERBS = {"push": True, "pop": False, "peek": False}


def _parse(op: str) -> Tuple[str, Optional[int]]:
    parts = op.replace(",", " ").split()
    if not parts:
        raise ValueError("Operação vazia.")
    verb = parts[0].lower()
    if verb not in _VERBS:
        raise ValueError(
            f"Operação '{verb}' inválida para pilha. Use: push <n>, pop, peek."
        )
    needs_arg = _VERBS[verb]
    if needs_arg:
        if len(parts) < 2:
            raise ValueError(f"'{verb}' exige um valor. Ex.: {verb} 5.")
        try:
            return verb, int(parts[1])
        except ValueError:
            raise ValueError(f"Argumento inválido em '{op}'.")
    return verb, None


def _top_ptr(stack: List[int]) -> dict:
    return {"top": len(stack) - 1} if stack else {}


def generate_stack_steps(
    operations: List[str], initial: Optional[List[int]] = None
) -> List[Step]:
    steps: List[Step] = []
    stack: List[int] = list(initial) if initial else []

    if stack:
        steps.append(
            Step(
                array_snapshot=stack.copy(),
                pointers=_top_ptr(stack),
                code_line=1,
                description=(
                    f"Estado atual da pilha: {len(stack)} elemento(s). "
                    f"Topo = {stack[-1]} (LIFO)."
                ),
            )
        )
    else:
        steps.append(
            Step(
                array_snapshot=[],
                code_line=1,
                description="Pilha vazia (política LIFO: o último a entrar é o primeiro a sair).",
            )
        )

    for op in operations:
        verb, arg = _parse(op)

        if verb == "push":
            steps.append(
                Step(
                    array_snapshot=stack.copy(),
                    pointers=_top_ptr(stack),
                    code_line=5,
                    description=f"push({arg}): inserindo {arg} no topo da pilha.",
                )
            )
            stack.append(arg)
            steps.append(
                Step(
                    array_snapshot=stack.copy(),
                    swapped_indices=[len(stack) - 1],
                    pointers=_top_ptr(stack),
                    code_line=6,
                    description=f"{arg} empilhado. Topo agora é o índice {len(stack) - 1}.",
                )
            )

        elif verb == "pop":
            if not stack:
                steps.append(
                    Step(
                        array_snapshot=[],
                        code_line=10,
                        description="pop(): a pilha está vazia, não há o que remover.",
                    )
                )
            else:
                top = len(stack) - 1
                steps.append(
                    Step(
                        array_snapshot=stack.copy(),
                        compared_indices=[top],
                        swapped_indices=[top],
                        pointers=_top_ptr(stack),
                        code_line=11,
                        description=f"pop(): removendo o elemento do topo ({stack[-1]}).",
                    )
                )
                stack.pop()
                tail = "Pilha vazia." if not stack else f"Novo topo: {stack[-1]}."
                steps.append(
                    Step(
                        array_snapshot=stack.copy(),
                        pointers=_top_ptr(stack),
                        code_line=11,
                        description=f"Elemento desempilhado. {tail}",
                    )
                )

        elif verb == "peek":
            if not stack:
                steps.append(
                    Step(
                        array_snapshot=[],
                        code_line=14,
                        description="peek(): a pilha está vazia.",
                    )
                )
            else:
                steps.append(
                    Step(
                        array_snapshot=stack.copy(),
                        compared_indices=[len(stack) - 1],
                        pointers=_top_ptr(stack),
                        code_line=14,
                        description=f"peek(): o topo é {stack[-1]} (consultado sem remover).",
                    )
                )

    steps.append(
        Step(
            array_snapshot=stack.copy(),
            pointers=_top_ptr(stack),
            description="Sequência de operações concluída.",
        )
    )
    return steps
