# Data Structures & Algorithms Visualizer

Platform for interactive visualization and learning of data structures and algorithms with real-time animations.

## Quick Start

### Requirements

- Docker & Docker Compose
- Node.js 18+ (optional, for running frontend without Docker)
- Python 3.11+ (optional, for running backend without Docker)

### Installation

```bash
git clone https://github.com/soueuabianca/mac0214.git
cd mac0214

# Run with Docker Compose
docker-compose up

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Architecture

The system uses a decoupled client-server architecture (SPA + REST API). The backend processes data structure algorithms deterministically, generating discrete sequences of execution states (snapshots). The frontend consumes and renders these animations in real-time using D3.js.

```
Frontend (React + Vite)
  - Header with navigation
  - D3.js canvas for visualization
  - Control panel (play, pause, speed)
  - Side panel (theory, code, comparison, quiz)
        |
        | HTTP/JSON
        |
Backend (FastAPI + Python)
  - /api/v1/sorting/  (Bubble, Quick, Merge, Heap, etc)
  - /api/v1/linear/   (Stack, Queue, Linked List)
  - /api/v1/trees/    (BST, AVL)
  - /api/v1/graphs/   (BFS, DFS, Dijkstra)
```

## Project Structure

```
mac0214/
├── backend/                 # FastAPI application
│   ├── main.py             # Main entry point
│   ├── schemas.py          # Pydantic models
│   ├── sorting/            # Sorting algorithms
│   │   ├── bubblesort.py
│   │   ├── quicksort.py
│   │   ├── mergesort.py
│   │   ├── heapsort.py
│   │   ├── selectionsort.py
│   │   ├── insertionsort.py
│   │   └── router.py
│   ├── linear/             # Linear data structures
│   │   ├── stack.py
│   │   ├── queue.py
│   │   ├── linkedlist.py
│   │   └── router.py
│   ├── trees/              # Tree structures
│   │   ├── bst.py          # Binary Search Tree
│   │   ├── avl.py          # AVL Tree
│   │   ├── common.py
│   │   └── router.py
│   └── graphs/             # Graph algorithms
│       ├── bfs.py
│       ├── dfs.py
│       ├── dijkstra.py
│       ├── common.py
│       └── router.py
├── frontend/               # React application
│   ├── src/
│   │   ├── main.js        # Entry point
│   │   ├── style.css
│   │   ├── api/
│   │   │   └── api.js     # API calls
│   │   └── engine/
│   │       └── renderer.js # D3.js rendering
│   ├── vite.config.js
│   ├── index.html
│   └── package.json
├── docker-compose.yml      # Container orchestration
├── package.json           # Project dependencies
└── README.md              # This file
```

## API Endpoints

### Sorting (`/api/v1/sorting/`)

| Algorithm | Endpoint | Method |
|-----------|----------|--------|
| Bubble Sort | `/bubble` | POST |
| Quick Sort | `/quick` | POST |
| Merge Sort | `/merge` | POST |
| Heap Sort | `/heap` | POST |
| Selection Sort | `/selection` | POST |
| Insertion Sort | `/insertion` | POST |

### Linear Structures (`/api/v1/linear/`)

| Structure | Endpoint |
|-----------|----------|
| Stack | `/stack` |
| Queue | `/queue` |
| Linked List | `/linkedlist` |

### Trees (`/api/v1/trees/`)

| Structure | Endpoint |
|-----------|----------|
| BST | `/bst` |
| AVL | `/avl` |

### Graphs (`/api/v1/graphs/`)

| Algorithm | Endpoint |
|-----------|----------|
| BFS | `/bfs` |
| DFS | `/dfs` |
| Dijkstra | `/dijkstra` |

Full API documentation available at `http://localhost:8000/docs`

## Technology Stack

### Backend
- FastAPI (Python 3.11+)
- Pydantic (data validation)
- Docker & Docker Compose

### Frontend
- React 18+
- Vite (build tool)
- D3.js (visualization)
- Fetch API (HTTP client)
- CSS3

## Development

### Adding a New Algorithm

1. Create the algorithm file in `backend/<category>/`

```python
def bubble_sort_steps(arr):
    steps = [{'array': arr.copy(), 'operation': 'start'}]
    
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            steps.append({
                'array': arr.copy(),
                'comparing': [j, j+1],
                'operation': 'compare'
            })
            
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                steps.append({
                    'array': arr.copy(),
                    'swapped': [j, j+1],
                    'operation': 'swap'
                })
    
    return steps
```

2. Create an endpoint in the corresponding `router.py`

```python
from fastapi import APIRouter
from ..schemas import AlgorithmRequest, AlgorithmResponse

router = APIRouter(prefix="/sorting", tags=["Sorting"])

@router.post("/bubble", response_model=AlgorithmResponse)
async def execute_bubble_sort(request: AlgorithmRequest):
    steps = bubble_sort_steps(request.array)
    return AlgorithmResponse(
        algorithm="Bubble Sort",
        steps=steps,
        complexity="O(n²)",
        space_complexity="O(1)"
    )
```

3. Register the router in `main.py`

```python
from .sorting.router import router as sorting_router
app.include_router(sorting_router, prefix="/api/v1")
```

## Roadmap

### Phase 1: Infrastructure (Complete)
- Project structure and directories
- Dockerfile and docker-compose.yml
- Git repository

### Phase 2: Backend (Complete)
- FastAPI with CORS configuration
- Algorithm implementations with step generation
- REST endpoints for all categories
- Swagger/OpenAPI documentation

### Phase 3: Frontend (In Progress)
- React SPA with Vite
- D3.js visualization setup
- Control panel and player
- API integration

### Phase 4: Pedagogy (Planned)
- Theory tab with explanations
- Code tab with syntax highlighting
- Comparison charts
- Interactive quizzes

### Phase 5: Polish (Planned)
- Responsive design
- Error handling
- Performance optimization
- Accessibility

## Contributing

1. Create a feature branch: `git checkout -b feature/name`
2. Make your changes and test locally
3. Commit with descriptive messages
4. Push to the repository
5. Open a pull request

## License

Educational use.
