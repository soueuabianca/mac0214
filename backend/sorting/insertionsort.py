from typing import List

from schemas import Step


def generate_insertion_sort_steps(arr: List[int]) -> List[Step]:
    steps = []
    current_arr = arr.copy()
    n = len(current_arr)

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            code_line=1,
            description="Estado inicial: array não ordenado.",
        )
    )

    for i in range(1, n):
        key = current_arr[i]
        j = i - 1

        steps.append(
            Step(
                array_snapshot=current_arr.copy(),
                active_range=[0, i],
                pointers={"i": i, "key_value": key},
                code_line=3,
                description=f"Selecionando a chave {key} no índice {i}.",
            )
        )

        while j >= 0 and current_arr[j] > key:
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[0, i],
                    compared_indices=[j, j + 1],
                    pointers={"i": i, "j": j},
                    code_line=5,
                    description=(
                        f"Comparando {current_arr[j]} com a chave em memória ({key})."
                    ),
                )
            )

            # Deslocamento para a direita
            current_arr[j + 1] = current_arr[j]

            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[0, i],
                    swapped_indices=[j + 1],
                    pointers={"i": i, "j": j},
                    code_line=6,
                    description=(
                        f"Deslocando {current_arr[j]} para a direita (índice {j + 1})."
                    ),
                )
            )
            j -= 1

        # Snapshot da última comparação que falha o loop, se aplicável
        if j >= 0:
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[0, i],
                    compared_indices=[j],
                    pointers={"i": i, "j": j},
                    code_line=5,
                    description=(
                        f"Comparando {current_arr[j]} com a chave ({key}). "
                        "Nenhum deslocamento necessário."
                    ),
                )
            )

        # Inserção da chave na posição correta
        current_arr[j + 1] = key
        steps.append(
            Step(
                array_snapshot=current_arr.copy(),
                active_range=[0, i],
                swapped_indices=[j + 1],
                pointers={"i": i, "j": j + 1},
                code_line=8,
                description=f"Inserindo a chave {key} na posição correta (índice {j + 1}).",
            )
        )

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            is_sorted=True,
            code_line=9,
            description="Ordenação concluída.",
        )
    )

    return steps
