import json
import re
import subprocess
import sys
from pathlib import Path

from app.agents.base_agent import BaseAgent
from app.generators.main_generator import MainGenerator


BACKEND_PACKAGE_CONTRACT = """
APPROVED GENERATED BACKEND MODULES:

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

REQUIRED INTERFACES:

app.database:
- Base
- engine
- SessionLocal
- get_db

app.models.user:
- User

app.models.project:
- Project

app.schemas.user:
- UserCreate
- UserUpdate
- UserRead

app.schemas.project:
- Project
- ProjectCreate
- ProjectUpdate

app.core.security:
- authenticate_user
- create_access_token
- get_current_user

ARCHITECTURE RULES:

1. Do not import modules outside this approved list.
2. Never import backend.app.*.
3. Never invent crud.py.
4. Never invent app.services.database.
5. Never import app.api.routes.models.
6. Never import app.api.routes.schemas.
7. Service modules contain business/database logic only.
8. FastAPI routes belong only under app.api.routes.
9. SQLAlchemy models are NOT FastAPI response_model classes.
10. FastAPI response_model must use Pydantic schemas.
11. Use absolute imports beginning with app.
12. Do not create new files not listed in the File Planner.
"""

class BackendAgent(BaseAgent):
    """Generate and validate approved backend files."""

    def __init__(self):
        super().__init__(
            "backend",
            "Senior FastAPI Backend Engineer",
            agent_key="backend",
        )

    async def run(self, task: str):
        return await self.develop_backend(task)

    def clean_code(self, code: str) -> str:
        """Extract only source code from an AI response."""

        code = str(code or "").strip()

        # Remove FILE: wrapper.
        code = re.sub(
            r"^\s*FILE:\s*[^\n]+\n",
            "",
            code,
            flags=re.IGNORECASE,
        )

        # Prefer content inside a Python fenced block.
        fenced = re.search(
            r"```(?:python|py)?\s*\n?(.*?)```",
            code,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if fenced:
            code = fenced.group(1).strip()

        # Remove common wrapper lines.
        lines = code.splitlines()

        while lines and lines[0].strip().lower() in {
            "python",
            "source code",
            "code:",
        }:
            lines.pop(0)

        while lines and lines[-1].strip() in {
            "===END===",
            "END",
        }:
            lines.pop()

        code = "\n".join(lines).strip()

        # Remove remaining fences.
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

        return code.replace("===END===", "").strip()

    @staticmethod
    def validate_import_contract(code: str):
        forbidden_patterns = [
            "backend.app.",
            "from . import crud",
            "from . import schemas",
            "from . import models",
            "from .database import",
            "from .auth import",
            "app.services.database",
            "app.services.crud",
            "app.api.routes.database",
            "app.api.routes.models",
            "app.api.routes.schemas",
        ]

        violations = [
            pattern
            for pattern in forbidden_patterns
            if pattern in code
        ]

        return violations
    def validate_python(self, filepath: Path):
        """Compile one generated Python file."""

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "py_compile",
                str(filepath),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return True, ""

        error = result.stderr.strip() or result.stdout.strip()
        return False, error

    async def repair_python(
        self,
        filepath: str,
        code: str,
        error: str,
    ):
        """Repair a generated Python file using targeted syntax feedback."""

        print(f"Repairing: {filepath}")

        # -------------------------------------------------
        # Deterministic fix for a common Python signature error:
        #
        # async def create_user(
        #     db: Session = Depends(get_db),
        #     user: schemas.UserCreate
        # )
        #
        # becomes:
        #
        # async def create_user(
        #     user: schemas.UserCreate,
        #     db: Session = Depends(get_db)
        # )
        # -------------------------------------------------

        if "parameter without a default follows parameter with a default" in error:
            repaired = re.sub(
                r"(\bdb\s*:\s*Session\s*=\s*Depends\(get_db\)\s*,\s*)"
                r"(user\s*:\s*schemas\.UserCreate)",
                r"\2, \1".rstrip(),
                code,
            )

            # Also handle the unqualified UserCreate form.
            repaired = re.sub(
                r"(\bdb\s*:\s*Session\s*=\s*Depends\(get_db\)\s*,\s*)"
                r"(user\s*:\s*(?:schemas\.)?UserCreate)",
                r"\2, db: Session = Depends(get_db)",
                repaired,
            )

            if repaired != code:
                return self.clean_code(repaired)

        # -------------------------------------------------
        # General targeted LLM repair
        # -------------------------------------------------

        prompt = f"""
You are a Python syntax repair specialist.

FILE:
{filepath}

PYTHON COMPILER ERROR:
{error}

CURRENT CODE:
{self._limit_text(code, 7000)}

TASK:
Return the COMPLETE corrected Python file.

STRICT RULES:
- Return ONLY Python source code.
- No FILE: prefix.
- No Markdown.
- No ``` fences.
- No explanations.
- Do not change unrelated functionality.
- The result MUST compile with Python 3.14.
- Preserve imports and existing interfaces where possible.

IMPORTANT PYTHON RULE:
A function parameter with a default value must not be followed by a
parameter without a default value.

For example, this is INVALID:
async def create_user(db: Session = Depends(get_db), user: UserCreate):

This is VALID:
async def create_user(user: UserCreate, db: Session = Depends(get_db)):

Return only the corrected file.
"""

        repaired = await self.think(prompt)

        repaired = self.clean_code(repaired)

        return repaired
    async def generate_file(
        self,
        filepath,
        task,
        ceo_summary,
        pm_plan,
        architecture,
    ):
        """Generate one approved backend file."""

        normalized = filepath.replace("\\", "/")

        # -------------------------------------------------
        # MAIN
        # -------------------------------------------------

        if normalized == "backend/app/main.py":
            generator = MainGenerator()

            return self.clean_code(
                await generator.generate(
                    filepath=filepath,
                    ceo_summary=ceo_summary,
                    project_plan=pm_plan,
                    architecture=architecture,
                    task=task,
                )
            )

        # -------------------------------------------------
        # CONFIG
        # -------------------------------------------------

        if normalized == "backend/app/core/config.py":
            return self.clean_code(
                """import os


class Settings:

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "AI Software Company",
    )

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./app.db",
    )

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "development-only-change-this",
    )

    ALGORITHM: str = os.getenv(
        "ALGORITHM",
        "HS256",
    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "30",
        )
    )

    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        "http://127.0.0.1:11434",
    )

    DEBUG: bool = (
        os.getenv("DEBUG", "false").lower()
        == "true"
    )


settings = Settings()


def get_settings():
    return settings
"""
            )

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        if normalized == "backend/app/database.py":
            return self.clean_code(
                """from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


DATABASE_URL = settings.DATABASE_URL

connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False,
    }

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
"""
            )

        # -------------------------------------------------
        # REQUIREMENTS
        # -------------------------------------------------

        if normalized == "backend/requirements.txt":
            return """fastapi
uvicorn[standard]
sqlalchemy
pydantic
python-multipart
python-jose[cryptography]
"""

        # -------------------------------------------------
        # DETERMINISTIC PROJECT SCHEMA
        # -------------------------------------------------

        if normalized == "backend/app/schemas/project.py":
            return self.clean_code(
                """from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class Project(ProjectBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class ProjectRead(Project):
    pass
"""

            )
        # -------------------------------------------------
        # OTHER APPROVED PYTHON FILES
        # -------------------------------------------------

        prompt = f"""
You are a senior Python FastAPI engineer.

Generate ONLY the complete Python source code for:

{filepath}

APPROVED BACKEND PACKAGE CONTRACT:

{BACKEND_PACKAGE_CONTRACT}

STRICT RULES:

- Return only valid Python source.
- No Markdown.
- No code fences.
- No FILE: prefix.
- Do not invent modules.
- Do not invent files.
- Use absolute imports beginning with app.
- Never import backend.app.*.
- Never invent crud.py.
- Never invent app.services.database.
- Never invent app.api.routes.models.
- Never invent app.api.routes.schemas.
- Service modules must not define FastAPI routes.
- SQLAlchemy models must not be FastAPI response_model classes.
- FastAPI response models must use Pydantic schemas.

CEO:
{self._limit_text(ceo_summary, 500)}

PM:
{self._limit_text(pm_plan, 600)}

ARCHITECTURE:
{self._limit_text(architecture, 800)}

TASK:
{self._limit_text(task, 300)}

Return ONLY valid Python source.
"""

        code = self.clean_code(
            await self.think(prompt)
        )

        violations = self.validate_import_contract(
            code
        )

        if violations:
            raise RuntimeError(
                f"Generated file {filepath} violates backend import contract: "
                + ", ".join(violations)
            )

        return code
    async def develop_backend(self, task: str):

        print("Backend Agent Started")

        # -------------------------------------------------
        # READ APPROVED UPSTREAM CONTEXT
        # -------------------------------------------------

        ceo_summary = (
            self.project_memory.read(
                "requirements/project_summary.md"
            )
            or memory_fallback(
                self.memory,
                "ceo",
            )
        )

        pm_plan = (
            self.project_memory.read(
                "project/pm_plan.md"
            )
            or self.memory.get("pm")
            or "Not provided in current project context."
        )

        architecture = (
            self.project_memory.read(
                "architecture/system_architecture.md"
            )
            or self.memory.get("cto")
            or "Not provided in current project context."
        )

        blueprint_text = (
            self.project_memory.read(
                "planning/file_list.md"
            )
        )

        # -------------------------------------------------
        # READ FILE BLUEPRINT
        # -------------------------------------------------

        try:
            blueprint = json.loads(blueprint_text)
            backend_files = blueprint.get("backend", [])
        except Exception as exc:
            print(f"Invalid blueprint: {exc}")
            backend_files = [
                "backend/app/main.py",
                "backend/requirements.txt",
            ]

        if not backend_files:
            raise RuntimeError(
                "File Planner returned no backend files."
            )

        print(
            f"Backend files approved: {len(backend_files)}"
        )

        generated = []

        output_root = Path("generated_code")
        output_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        # -------------------------------------------------
        # GENERATE FILES
        # -------------------------------------------------

        for index, filepath in enumerate(
            backend_files,
            start=1,
        ):

            print("=" * 60)
            print(
                f"Generating {index}/{len(backend_files)}"
            )
            print(filepath)
            print("=" * 60)

            code = await self.generate_file(
                filepath=filepath,
                task=task,
                ceo_summary=ceo_summary,
                pm_plan=pm_plan,
                architecture=architecture,
            )

            output_file = output_root / filepath

            output_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            output_file.write_text(
                code,
                encoding="utf-8",
            )

            # -------------------------------------------------
            # VALIDATE + REPAIR
            # -------------------------------------------------

            max_repairs = 2
            valid = False

            for attempt in range(
                max_repairs + 1
            ):

                valid, error = self.validate_python(
                    output_file
                )

                if valid:
                    print(
                        f"VALID: {filepath}"
                    )
                    break

                print(
                    f"INVALID: {filepath}"
                )
                print(error)

                if attempt >= max_repairs:
                    raise RuntimeError(
                        f"Could not repair {filepath} "
                        f"after {max_repairs} attempts."
                    )

                code = await self.repair_python(
                    filepath=filepath,
                    code=code,
                    error=error,
                )

                output_file.write_text(
                    code,
                    encoding="utf-8",
                )

            # -------------------------------------------------
            # SAVE ONLY VALIDATED CODE
            # -------------------------------------------------

            if not valid:
                raise RuntimeError(
                    f"Generated file is not valid: {filepath}"
                )

            self.project_memory.write(
                filepath,
                code,
            )

            print(
                f"Saved: {output_file}"
            )

            generated.append(filepath)

        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        backend_result = json.dumps(
            {
                "generated_files": generated,
                "count": len(generated),
                "status": "completed",
            },
            indent=4,
        )

        self.memory.save(
            "backend",
            backend_result,
        )

        self.project_memory.write(
            "backend/backend_generation_result.md",
            backend_result,
        )

        print()
        print("=" * 60)
        print("Backend Generation Complete")
        print(
            f"Generated {len(generated)} backend files."
        )
        print("=" * 60)

        return generated

    @staticmethod
    def _limit_text(value: str, maximum: int) -> str:
        value = str(value or "")

        if len(value) <= maximum:
            return value

        return (
            value[:maximum]
            + "\n[Context truncated.]"
        )


def memory_fallback(memory_obj, key: str) -> str:
    """Safely read a value from project memory."""

    try:
        value = memory_obj.get(key)
    except Exception:
        value = ""

    return value or "Not provided in current project context."



















