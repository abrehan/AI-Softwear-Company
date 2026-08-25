from app.api.routes.workflow import router as workflow_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

# Import models so SQLAlchemy knows about them
from app.models.user import User
from app.models.project import Project

# Working API routers
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.projects import router as projects_router
from app.api.routes.departments import router as departments_router
from app.api.routes.agents import router as agents_router
from app.api.routes.registry import router as registry_router
from app.api.routes.ai import router as ai_router
from app.models.department import Department
from app.models.agent import Agent

app = FastAPI(
    title="AI Software Company",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# ROUTES
# --------------------------------------------------

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)
app.include_router(departments_router)
app.include_router(agents_router)
app.include_router(registry_router)
app.include_router(ai_router)


# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "AI Software Company",
        "version": app.version,
        "status": "online",
    }


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }






# --------------------------------------------------
# API HEALTH
# --------------------------------------------------

@app.get("/api/health")
def api_health():
    return {
        "status": "healthy",
    }





# --------------------------------------------------
# API STATUS
# --------------------------------------------------

@app.get("/api/status")
def api_status():
    return {
        "name": "AI Software Company",
        "version": app.version,
        "backend": "online",
        "status": "healthy",
    }

app.include_router(workflow_router)


