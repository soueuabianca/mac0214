from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class TreeNode(BaseModel):
    """Nó de árvore binária para visualização (usado em BST e AVL).

    Estrutura aninhada: cada nó carrega suas subárvores. O front-end reenvia
    esta mesma estrutura como estado inicial para preservar a árvore entre
    operações interativas (round-trip exato, inclusive após remoções).
    """
    value: int
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None
    state: str = Field(
        default="normal",
        description="Realce do nó: normal|compared|active|inserted|found|removed|visited.",
    )
    height: Optional[int] = Field(default=None, description="Altura do nó (apenas AVL).")
    balance: Optional[int] = Field(default=None, description="Fator de balanceamento (apenas AVL).")


class GraphNode(BaseModel):
    """Vértice para visualização de grafo. x/y são posições relativas (0..1)."""
    id: int
    x: float = Field(default=0.5, description="Posição horizontal relativa (0..1).")
    y: float = Field(default=0.5, description="Posição vertical relativa (0..1).")
    state: str = Field(
        default="normal",
        description="Realce: normal|source|current|frontier|visited|target|inpath.",
    )
    dist: Optional[float] = Field(default=None, description="Distância/rótulo do vértice (BFS/Dijkstra).")


class GraphEdge(BaseModel):
    u: int
    v: int
    weight: Optional[float] = Field(default=None, description="Peso da aresta (None = não ponderada).")
    state: str = Field(
        default="normal",
        description="Realce: normal|considered|tree|inpath.",
    )


class GraphSnapshot(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)
    directed: bool = Field(default=False, description="Se as arestas têm direção.")


class Step(BaseModel):
    array_snapshot: List[int] = Field(..., description="Estado exato do array neste frame.")
    compared_indices: List[int] = Field(default_factory=list, description="Índices sendo comparados (renderizar com cor de aviso).")
    swapped_indices: List[int] = Field(default_factory=list, description="Índices que sofreram troca (renderizar com cor de ação).")
    active_range: Optional[List[int]] = Field(default=None, description="Tupla [inicio, fim] do sub-array em foco. O D3.js deve esmaecer o resto do array.")
    pointers: Dict[str, int] = Field(default_factory=dict, description="Ponteiros fixos. Ex: {'pivot': 4, 'i': 2, 'j': 5}.")
    is_sorted: bool = Field(default=False, description="Flag de conclusão geral.")
    code_line: Optional[int] = Field(default=None, description="Linha (1-indexada) do array 'code' que este passo executa. Usado pelo destaque dinâmico da aba Código.")
    description: str = Field(default="", description="Explicação passo-a-passo para o Painel Lateral.")
    tree: Optional[TreeNode] = Field(default=None, description="Raiz da árvore neste frame (visualização de árvores). None = árvore vazia.")
    graph: Optional[GraphSnapshot] = Field(default=None, description="Grafo neste frame (visualização de grafos), com estados por nó/aresta.")

class AlgorithmResponse(BaseModel):
    algorithm: str
    steps: List[Step]

class QuizItem(BaseModel):
    question: str = Field(..., description="Pergunta do quiz.")
    options: List[str] = Field(..., description="Lista de alternativas.")
    answer: int = Field(..., description="Índice da alternativa correta (0 a N).")
    explanation: str = Field(..., description="Explicação pedagógica da resposta.")

class Theory(BaseModel):
    description: str
    time_complexity: str = Field(..., description="Notação Big-O para tempo.")
    space_complexity: str = Field(..., description="Notação Big-O para espaço.")

class MetadataResponse(BaseModel):
    algorithm: str
    theory: Theory
    code: List[str] = Field(default_factory=list, description="Código-fonte exibido na aba Código, uma string por linha (1-indexada).")
    quiz: List[QuizItem]

class ArrayInput(BaseModel):
    data: List[int] = Field(..., description="Array de números inteiros para ordenação.")

class OperationInput(BaseModel):
    operations: List[str] = Field(
        ...,
        description="Sequência de operações. Ex.: ['push 5', 'push 8', 'pop'].",
    )
    initial: List[int] = Field(
        default_factory=list,
        description=(
            "Estado inicial da estrutura sobre o qual as operações serão aplicadas. "
            "Permite executar uma única operação de forma interativa preservando o "
            "conteúdo atual (o front-end mantém o estado e o reenvia)."
        ),
    )


class TreeOperationInput(BaseModel):
    operations: List[str] = Field(
        ...,
        description=(
            "Operações sobre a árvore. Ex.: ['insert 5', 'search 8', 'delete 3', "
            "'traverse inorder']."
        ),
    )
    initial: Optional[TreeNode] = Field(
        default=None,
        description=(
            "Árvore atual (raiz) reenviada pelo front-end para preservar o estado "
            "entre operações. None = árvore vazia."
        ),
    )


class GraphInput(BaseModel):
    graph: GraphSnapshot = Field(..., description="Grafo sobre o qual o algoritmo será executado.")
    source: int = Field(default=0, description="Vértice de origem.")
    target: Optional[int] = Field(default=None, description="Vértice de destino (opcional, p/ realçar caminho).")


# Resolve a auto-referência de TreeNode (pydantic v2).
TreeNode.model_rebuild()