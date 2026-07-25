from typing import List

from schemas import Step


def generate_quick_sort_steps(arr: List[int]) -> List[Step]:
    steps = []
    current_arr = arr.copy()

    def quicksort(low: int, high: int):
        if low < high:
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[low, high],
                    code_line=2,
                    description=(
                        f"Iniciando Quick Sort na partição de índice {low} a {high}."
                    ),
                )
            )
            pi = partition(low, high)
            quicksort(low, pi - 1)
            quicksort(pi + 1, high)

    def partition(low: int, high: int) -> int:
        pivot = current_arr[high]
        i = low - 1

        steps.append(
            Step(
                array_snapshot=current_arr.copy(),
                active_range=[low, high],
                pointers={"pivot": high, "i": i},
                code_line=8,
                description=f"Pivô escolhido: {pivot} (índice {high}).",
            )
        )

        for j in range(low, high):
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[low, high],
                    compared_indices=[j, high],
                    pointers={"pivot": high, "i": i, "j": j},
                    code_line=11,
                    description=f"Comparando {current_arr[j]} com o pivô {pivot}.",
                )
            )

            if current_arr[j] < pivot:
                i += 1
                current_arr[i], current_arr[j] = current_arr[j], current_arr[i]
                steps.append(
                    Step(
                        array_snapshot=current_arr.copy(),
                        active_range=[low, high],
                        swapped_indices=[i, j] if i != j else [],
                        pointers={"pivot": high, "i": i, "j": j},
                        code_line=13,
                        description=f"Menor que o pivô. Trocando índices {i} e {j}.",
                    )
                )

        current_arr[i + 1], current_arr[high] = current_arr[high], current_arr[i + 1]
        steps.append(
            Step(
                array_snapshot=current_arr.copy(),
                active_range=[low, high],
                swapped_indices=[i + 1, high],
                pointers={"pivot": i + 1},
                code_line=14,
                description=(
                    f"Posicionando o pivô {pivot} no local definitivo (índice {i + 1})."
                ),
            )
        )
        return i + 1

    quicksort(0, len(current_arr) - 1)

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            is_sorted=True,
            code_line=15,
            description="Ordenação concluída.",
        )
    )
    return steps
