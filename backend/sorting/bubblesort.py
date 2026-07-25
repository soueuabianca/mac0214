from typing import List

from schemas import Step

# As linhas de código exibidas na aba "Código" estão em data/sorting.json.
# O campo code_line abaixo (1-indexado) aponta para a linha correspondente.


def generate_bubble_sort_steps(arr: List[int]) -> List[Step]:
    steps = []
    n = len(arr)
    current_arr = arr.copy()

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            code_line=1,
            description="Estado inicial: array não ordenado.",
        )
    )

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            # Snapshot de comparação
            steps.append(
                Step(
                    array_snapshot=current_arr.copy(),
                    compared_indices=[j, j + 1],
                    code_line=6,
                    description=(
                        f"Comparando índices {j} (valor {current_arr[j]}) "
                        f"e {j + 1} (valor {current_arr[j + 1]})."
                    ),
                )
            )

            if current_arr[j] > current_arr[j + 1]:
                current_arr[j], current_arr[j + 1] = (
                    current_arr[j + 1],
                    current_arr[j],
                )
                swapped = True

                # Snapshot de troca
                steps.append(
                    Step(
                        array_snapshot=current_arr.copy(),
                        swapped_indices=[j, j + 1],
                        code_line=7,
                        description=(
                            f"Troca realizada: {current_arr[j]} agora precede "
                            f"{current_arr[j + 1]}."
                        ),
                    )
                )

        if not swapped:
            break  # Otimização: a estrutura já está ordenada

    steps.append(
        Step(
            array_snapshot=current_arr.copy(),
            is_sorted=True,
            code_line=11,
            description="Ordenação concluída.",
        )
    )

    return steps
