from typing import List, Optional, Tuple

from schemas import Step

_VERBS = {"insert": True, "delete": True, "search": True}


def _parse(op: str) -> Tuple[str, Optional[int]]:
    parts = op.replace(",", " ").split()
    if not parts:
        raise ValueError("Operação vazia.")
    verb = parts[0].lower()
    if verb not in _VERBS:
        raise ValueError(
            f"Operação '{verb}' inválida para lista encadeada. "
            "Use: insert <n>, delete <n>, search <n>."
        )
    if len(parts) < 2:
        raise ValueError(f"'{verb}' exige um valor. Ex.: {verb} 5.")
    try:
        return verb, int(parts[1])
    except ValueError:
        raise ValueError(f"Argumento inválido em '{op}'.")


def _head_ptr(lst: List[int]) -> dict:
    return {"head": 0} if lst else {}


def generate_linked_list_steps(
    operations: List[str], initial: Optional[List[int]] = None
) -> List[Step]:
    steps: List[Step] = []
    lst: List[int] = list(initial) if initial else []

    if lst:
        steps.append(
            Step(
                array_snapshot=lst.copy(),
                pointers=_head_ptr(lst),
                code_line=8,
                description=(
                    f"Estado atual da lista: {len(lst)} nó(s). head = {lst[0]}."
                ),
            )
        )
    else:
        steps.append(
            Step(
                array_snapshot=[],
                code_line=8,
                description="Lista encadeada vazia (head aponta para None).",
            )
        )

    for op in operations:
        verb, arg = _parse(op)

        if verb == "insert":
            steps.append(
                Step(
                    array_snapshot=lst.copy(),
                    pointers=_head_ptr(lst),
                    code_line=11,
                    description=f"insert({arg}): criando um novo nó com valor {arg}.",
                )
            )
            if not lst:
                lst.append(arg)
                steps.append(
                    Step(
                        array_snapshot=lst.copy(),
                        swapped_indices=[0],
                        pointers=_head_ptr(lst),
                        code_line=13,
                        description=f"Lista vazia: o novo nó {arg} vira o head.",
                    )
                )
            else:
                # Percorre até o último nó.
                for i in range(len(lst)):
                    steps.append(
                        Step(
                            array_snapshot=lst.copy(),
                            compared_indices=[i],
                            pointers={"head": 0, "cur": i},
                            code_line=16,
                            description=(
                                f"Percorrendo até o fim: cur no índice {i} "
                                f"(valor {lst[i]})."
                            ),
                        )
                    )
                lst.append(arg)
                steps.append(
                    Step(
                        array_snapshot=lst.copy(),
                        swapped_indices=[len(lst) - 1],
                        pointers={"head": 0, "cur": len(lst) - 1},
                        code_line=18,
                        description=f"{arg} inserido no fim (índice {len(lst) - 1}).",
                    )
                )

        elif verb == "search":
            found = False
            for i in range(len(lst)):
                match = lst[i] == arg
                steps.append(
                    Step(
                        array_snapshot=lst.copy(),
                        compared_indices=[i],
                        swapped_indices=[i] if match else [],
                        pointers={"head": 0, "cur": i},
                        code_line=24,
                        description=(
                            f"search({arg}): comparando com o nó {i} (valor {lst[i]})."
                            + (" Encontrado!" if match else "")
                        ),
                    )
                )
                if match:
                    found = True
                    steps.append(
                        Step(
                            array_snapshot=lst.copy(),
                            swapped_indices=[i],
                            pointers={"head": 0, "cur": i},
                            code_line=25,
                            description=f"Valor {arg} encontrado no índice {i}.",
                        )
                    )
                    break
            if not found:
                steps.append(
                    Step(
                        array_snapshot=lst.copy(),
                        pointers=_head_ptr(lst),
                        code_line=28,
                        description=f"Valor {arg} não encontrado. Retorna -1.",
                    )
                )

        elif verb == "delete":
            target = None
            for i in range(len(lst)):
                match = lst[i] == arg
                steps.append(
                    Step(
                        array_snapshot=lst.copy(),
                        compared_indices=[i],
                        pointers={"head": 0, "cur": i},
                        code_line=34,
                        description=(
                            f"delete({arg}): comparando com o nó {i} (valor {lst[i]})."
                        ),
                    )
                )
                if match:
                    target = i
                    break
            if target is None:
                steps.append(
                    Step(
                        array_snapshot=lst.copy(),
                        pointers=_head_ptr(lst),
                        code_line=38,
                        description=f"Valor {arg} não está na lista, nada a remover.",
                    )
                )
            else:
                # Remover o head (índice 0) usa uma linha diferente da remoção no meio.
                relink_line = 43 if target == 0 else 41
                steps.append(
                    Step(
                        array_snapshot=lst.copy(),
                        swapped_indices=[target],
                        pointers={"head": 0, "cur": target},
                        code_line=relink_line,
                        description=(
                            f"Religando o ponteiro para pular o nó {target} (valor {arg})."
                        ),
                    )
                )
                lst.pop(target)
                steps.append(
                    Step(
                        array_snapshot=lst.copy(),
                        pointers=_head_ptr(lst),
                        code_line=relink_line,
                        description=f"Nó com valor {arg} removido da lista.",
                    )
                )

    steps.append(
        Step(
            array_snapshot=lst.copy(),
            pointers=_head_ptr(lst),
            description="Sequência de operações concluída.",
        )
    )
    return steps
