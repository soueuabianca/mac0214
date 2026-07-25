from typing import List, Optional, Tuple

from schemas import Step

_VERBS = {"enqueue": True, "dequeue": False, "front": False}


def _parse(op: str) -> Tuple[str, Optional[int]]:
    parts = op.replace(",", " ").split()
    if not parts:
        raise ValueError("Operação vazia.")
    verb = parts[0].lower()
    if verb not in _VERBS:
        raise ValueError(
            f"Operação '{verb}' inválida para fila. "
            "Use: enqueue <n>, dequeue, front."
        )
    if _VERBS[verb]:
        if len(parts) < 2:
            raise ValueError(f"'{verb}' exige um valor. Ex.: {verb} 5.")
        try:
            return verb, int(parts[1])
        except ValueError:
            raise ValueError(f"Argumento inválido em '{op}'.")
    return verb, None


def _ptrs(queue: List[int]) -> dict:
    if not queue:
        return {}
    return {"front": 0, "rear": len(queue) - 1}


def generate_queue_steps(
    operations: List[str], initial: Optional[List[int]] = None
) -> List[Step]:
    steps: List[Step] = []
    queue: List[int] = list(initial) if initial else []

    if queue:
        steps.append(
            Step(
                array_snapshot=queue.copy(),
                pointers=_ptrs(queue),
                code_line=1,
                description=(
                    f"Estado atual da fila: {len(queue)} elemento(s). "
                    f"Frente = {queue[0]} (FIFO)."
                ),
            )
        )
    else:
        steps.append(
            Step(
                array_snapshot=[],
                code_line=1,
                description="Fila vazia (política FIFO: o primeiro a entrar é o primeiro a sair).",
            )
        )

    for op in operations:
        verb, arg = _parse(op)

        if verb == "enqueue":
            steps.append(
                Step(
                    array_snapshot=queue.copy(),
                    pointers=_ptrs(queue),
                    code_line=5,
                    description=f"enqueue({arg}): inserindo {arg} no final (rear).",
                )
            )
            queue.append(arg)
            steps.append(
                Step(
                    array_snapshot=queue.copy(),
                    swapped_indices=[len(queue) - 1],
                    pointers=_ptrs(queue),
                    code_line=6,
                    description=f"{arg} enfileirado. Rear agora é o índice {len(queue) - 1}.",
                )
            )

        elif verb == "dequeue":
            if not queue:
                steps.append(
                    Step(
                        array_snapshot=[],
                        code_line=10,
                        description="dequeue(): a fila está vazia, não há o que remover.",
                    )
                )
            else:
                steps.append(
                    Step(
                        array_snapshot=queue.copy(),
                        compared_indices=[0],
                        swapped_indices=[0],
                        pointers=_ptrs(queue),
                        code_line=11,
                        description=f"dequeue(): removendo o elemento da frente ({queue[0]}).",
                    )
                )
                queue.pop(0)
                tail = "Fila vazia." if not queue else f"Nova frente: {queue[0]}."
                steps.append(
                    Step(
                        array_snapshot=queue.copy(),
                        pointers=_ptrs(queue),
                        code_line=11,
                        description=f"Elemento desenfileirado. {tail}",
                    )
                )

        elif verb == "front":
            if not queue:
                steps.append(
                    Step(
                        array_snapshot=[],
                        code_line=14,
                        description="front(): a fila está vazia.",
                    )
                )
            else:
                steps.append(
                    Step(
                        array_snapshot=queue.copy(),
                        compared_indices=[0],
                        pointers=_ptrs(queue),
                        code_line=14,
                        description=f"front(): a frente é {queue[0]} (consultada sem remover).",
                    )
                )

    steps.append(
        Step(
            array_snapshot=queue.copy(),
            pointers=_ptrs(queue),
            description="Sequência de operações concluída.",
        )
    )
    return steps
