from app.services.ollama_service import OllamaService
from app.services.model_router import ModelRouter
import re


class MainGenerator:

    def __init__(self):
        self.ai = OllamaService()
        self.model = ModelRouter.get("backend")

    async def generate(
        self,
        filepath,
        ceo_summary,
        project_plan,
        architecture,
        task,
    ):

        # --------------------------------------------------
        # Deterministic application entry point.
        # Do not let the LLM invent router/package imports.
        # --------------------------------------------------

        if filepath.replace("\\", "/") == "backend/app/main.py":
            return self.generate_main()

        prompt = f"""
You are a senior Python FastAPI engineer.

Generate ONLY the complete Python source code for:

{filepath}

IMPORTANT:
- Return ONLY Python source code.
- No Markdown.
- No ``` fences.
- No FILE: prefix.
- No explanations.
- Do not invent modules.
- Do not invent package names.

APPROVED PACKAGE CONTRACT:

Available modules are ONLY:

app.database
app.core.config
app.core.security
app.models.user
app.models.project
app.schemas.user
app.schemas.project
app.api.routes.auth
app.api.routes.users
app.api.routes.projects
app.services.auth_service
app.services.user_service
app.services.project_service
app.utils.helpers

IMPORTANT INTERFACES:

app.database MUST expose:
- Base
- engine
- SessionLocal
- get_db

app.models.user MUST expose:
- User

app.models.project MUST expose:
- Project

app.schemas.user MUST expose:
- UserCreate
- UserUpdate
- UserRead

app.schemas.project MUST expose:
- Project
- ProjectCreate
- ProjectUpdate

app.core.security MUST expose:
- authenticate_user
- create_access_token
- get_current_user

Do NOT import:
- crud
- app.services.crud
- app.services.database
- app.api.routes.models
- app.api.routes.schemas
- backend.app.*
- any module not listed above

SERVICE RULE:
Service files contain database/business logic only.
They MUST NOT define FastAPI routes.

ROUTE RULE:
FastAPI routes belong only in:
- app.api.routes.auth
- app.api.routes.users
- app.api.routes.projects

PROJECT CONTEXT:
{ceo_summary[:500]}

PROJECT PLAN:
{project_plan[:600]}

ARCHITECTURE:
{architecture[:800]}

TASK:
{task[:300]}

Return ONLY valid Python source code.
"""

        code = await self.ai.generate(
            prompt,
            self.model,
        )

        return self.clean_code(code)

    @staticmethod
    def generate_main() -> str:

        return '''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine

from app.models.user import User
from app.models.project import Project

from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.api.routes.projects import router as projects_router


app = FastAPI(
    title="AI Software Company",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


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


Base.metadata.create_all(bind=engine)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(projects_router)


@app.get("/")
def root():
    return {
        "name": "AI Software Company",
        "version": app.version,
        "status": "online",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/api/health")
def api_health():
    return {
        "status": "healthy",
    }
'''

    @staticmethod
    def clean_code(code: str) -> str:

        code = str(code or "").strip()

        code = re.sub(
            r"^\s*FILE:\s*[^\n]+\n",
            "",
            code,
            flags=re.IGNORECASE,
        )

        fenced = re.search(
            r"```(?:python|py)?\s*\n?(.*?)```",
            code,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if fenced:
            code = fenced.group(1).strip()

        if code.strip() == "backend/app/main.py":
            return ""

        code = re.sub(
            r"^\s*```(?:python|py)?\s*",
            "",
            code,
            flags=re.IGNORECASE,
        )

        code = re.sub(
            r"\s*```\s*$",
            "",
            code,
            flags=re.IGNORECASE,
        )

        return code.strip()
