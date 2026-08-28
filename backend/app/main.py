from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

from app.api.routes.projects import router as project_router
from app.api.routes.tasks import router as task_router
from app.api.routes.auth import router as auth_router
from app.persistence import store

app = FastAPI(
    title="AI Software Company",
    version="1.0.0"
)

@app.on_event("startup")
async def initialize_storage():
    store.initialize()

# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# API ROUTES
# ==========================================

app.include_router(project_router, prefix="/api")
app.include_router(task_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

# ==========================================
# ROOT
# ==========================================

@app.get("/")
async def root():
    return {
        "message": "AI Software Company Backend Running"
    }
# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/api/health")
async def health():
    return {
        "status": "healthy"
    }

# ==========================================
# SYSTEM STATUS
# ==========================================

@app.get("/api/status")
async def status():

    ollama = "Offline"

    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(
                "http://127.0.0.1:11434/api/tags"
            )

            if response.status_code == 200:
                ollama = "Online"

    except Exception:
        ollama = "Offline"

    database = "SQLite connected"

    return {
        "version": app.version,
        "backend": "Online",
        "frontend": "Online",
        "ollama": ollama,
        "database": database,
        "system": "Healthy"
    }
