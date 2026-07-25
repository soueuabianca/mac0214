from typing import List

from schemas import Step


def generate_merge_sort_steps(arr: List[int]) -> List[Step]:
    steps = []
    current_arr = arr.copy()

    def merge_sort(left: int, right: int):
        if left < right:
            mid = (left + right) // 2

            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[left, right],
                    pointers={"mid": mid},
                    code_line=3,
                    description=(
                        f"Dividindo o array na metade (índices {left} a {right})."
                    ),
                )
            )

            merge_sort(left, mid)
            merge_sort(mid + 1, right)
            merge(left, mid, right)

    def merge(left: int, mid: int, right: int):
        L = current_arr[left : mid + 1]
        R = current_arr[mid + 1 : right + 1]

        steps.append(
            Step(
                array_snapshot=current_arr.copy(),
                active_range=[left, right],
                code_line=8,
                description=(
                    f"Iniciando mesclagem das partições left={L} e right={R}."
                ),
            )
        )

        i = j = 0
        k = left

        while i < len(L) and j < len(R):
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[left, right],
                    pointers={"k": k},
                    code_line=14,
                    description=f"Avaliando inserção: {L[i]} (esq) vs {R[j]} (dir).",
                )
            )

            if L[i] <= R[j]:
                current_arr[k] = L[i]
                i += 1
            else:
                current_arr[k] = R[j]
                j += 1

            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[left, right],
                    swapped_indices=[k],
                    pointers={"k": k},
                    code_line=15,
                    description=(
                        f"Sobrescrevendo índice {k} com o valor {current_arr[k]}."
                    ),
                )
            )
            k += 1

        while i < len(L):
            current_arr[k] = L[i]
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[left, right],
                    swapped_indices=[k],
                    pointers={"k": k},
                    code_line=20,
                    description=(
                        f"Esgotamento da partição direita. Inserindo "
                        f"{current_arr[k]} no índice {k}."
                    ),
                )
            )
            i += 1
            k += 1

        while j < len(R):
            current_arr[k] = R[j]
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    active_range=[left, right],
                    swapped_indices=[k],
                    pointers={"k": k},
                    code_line=22,
                    description=(
                        f"Esgotamento da partição esquerda. Inserindo "
                        f"{current_arr[k]} no índice {k}."
                    ),
                )
            )
            j += 1
            k += 1

    merge_sort(0, len(current_arr) - 1)

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            is_sorted=True,
            code_line=1,
            description="Ordenação concluída.",
        )
    )
    return steps
