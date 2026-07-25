from typing import List

from schemas import Step


def generate_selection_sort_steps(arr: List[int]) -> List[Step]:
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

    for i in range(n):
        min_idx = i

        steps.append(
            Step(
                array_snapshot=current_arr.copy(),
                active_range=[i, n - 1],
                pointers={"i": i, "min_idx": min_idx},
                code_line=4,
                description=(
                    f"Buscando menor elemento a partir do índice {i}. "
                    f"Atual min: {current_arr[min_idx]}."
                ),
            )
        )

        for j in range(i + 1, n):
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[i, n - 1],
                    compared_indices=[j, min_idx],
                    pointers={"i": i, "min_idx": min_idx, "j": j},
                    code_line=6,
                    description=(
                        f"Comparando atual {current_arr[j]} com o menor "
                        f"encontrado {current_arr[min_idx]}."
                    ),
                )
            )

            if current_arr[j] < current_arr[min_idx]:
                min_idx = j
                steps.append(
                    Step(
                        array_snapshot=current_arr.copy(),
                        active_range=[i, n - 1],
                        pointers={"i": i, "min_idx": min_idx, "j": j},
                        code_line=7,
                        description=(
                            f"Novo menor elemento encontrado: {current_arr[min_idx]} "
                            f"no índice {min_idx}."
                        ),
                    )
                )

        if min_idx != i:
            current_arr[i], current_arr[min_idx] = (
                current_arr[min_idx],
                current_arr[i],
            )
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[i, n - 1],
                    swapped_indices=[i, min_idx],
                    pointers={"i": i, "min_idx": min_idx},
                    code_line=8,
                    description=(
                        f"Trocando {current_arr[i]} (índice {i}) com "
                        f"{current_arr[min_idx]} (índice {min_idx})."
                    ),
                )
            )
        else:
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[i, n - 1],
                    pointers={"i": i},
                    code_line=8,
                    description=(
                        f"O menor elemento já está na posição correta (índice {i})."
                    ),
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
