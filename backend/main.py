from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Importações Ativas ---
from sorting.router import router as sorting_router

# --- Importações Ativas ---
from linear.router import router as linear_router
from trees.router import router as trees_router
from graphs.router import router as graphs_router

app = FastAPI(title="Algorithm Visualizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rotas Funcionais ---
app.include_router(sorting_router, prefix="/api/v1/sorting", tags=["Sorting"])
app.include_router(linear_router, prefix="/api/v1/linear", tags=["Linear"])
app.include_router(trees_router, prefix="/api/v1/trees", tags=["Trees"])
app.include_router(graphs_router, prefix="/api/v1/graphs", tags=["Graphs"])

@app.get("/")
def read_root():
    """Endpoint de health-check básico."""
    return {"status": "Algorithm Visualizer API is running"}