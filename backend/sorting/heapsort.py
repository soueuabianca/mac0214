from typing import List

from schemas import Step


def generate_heap_sort_steps(arr: List[int]) -> List[Step]:
    steps = []
    current_arr = arr.copy()
    n = len(current_arr)

    def heapify(heap_size: int, root_idx: int):
        largest = root_idx
        left = 2 * root_idx + 1
        right = 2 * root_idx + 2

        steps.append(
            Step(
                array_snapshot=current_arr.copy(),
                active_range=[0, heap_size - 1],
                pointers={"root": root_idx, "largest": largest},
                code_line=11,
                description=(
                    f"Analisando nó raiz {current_arr[root_idx]} no índice {root_idx}."
                ),
            )
        )

        if left < heap_size:
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[0, heap_size - 1],
                    compared_indices=[left, largest],
                    pointers={"root": root_idx, "left": left, "largest": largest},
                    code_line=14,
                    description=(
                        f"Comparando filho esquerdo {current_arr[left]} com "
                        f"{current_arr[largest]}."
                    ),
                )
            )
            if current_arr[left] > current_arr[largest]:
                largest = left

        if right < heap_size:
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[0, heap_size - 1],
                    compared_indices=[right, largest],
                    pointers={"root": root_idx, "right": right, "largest": largest},
                    code_line=16,
                    description=(
                        f"Comparando filho direito {current_arr[right]} com "
                        f"{current_arr[largest]}."
                    ),
                )
            )
            if current_arr[right] > current_arr[largest]:
                largest = right

        if largest != root_idx:
            current_arr[root_idx], current_arr[largest] = (
                current_arr[largest],
                current_arr[root_idx],
            )
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[0, heap_size - 1],
                    swapped_indices=[root_idx, largest],
                    pointers={"root": root_idx, "largest": largest},
                    code_line=19,
                    description=(
                        f"Propriedade do Heap violada. Trocando índice {root_idx} "
                        f"com {largest}."
                    ),
                )
            )
            heapify(heap_size, largest)

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            code_line=3,
            description="Iniciando a construção do Max Heap.",
        )
    )

    # Construção do Max Heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            code_line=5,
            description="Max Heap construído. Iniciando extração das raízes.",
        )
    )

    # Extração de elementos
    for i in range(n - 1, 0, -1):
        current_arr[i], current_arr[0] = current_arr[0], current_arr[i]
        steps.append(
            Step(
                array_snapshot=current_arr.copy(),
                active_range=[0, i],
                swapped_indices=[0, i],
                pointers={"i": i},
                code_line=6,
                description=(
                    f"Movendo o maior elemento para o final do sub-array "
                    f"(índices 0 e {i})."
                ),
            )
        )
        heapify(i, 0)

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            is_sorted=True,
            code_line=8,
            description="Ordenação concluída.",
        )
    )

    return steps
