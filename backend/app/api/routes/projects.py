from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.persistence import store

router = APIRouter(prefix="/projects", tags=["Projects"])


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    brief: str = Field(min_length=10, max_length=10_000)
    client: str | None = Field(default=None, max_length=120)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    brief: str | None = Field(default=None, min_length=10, max_length=10_000)
    status: str | None = Field(default=None, pattern="^(discovery|planning|building|review|shipped|archived)$")


@router.get("")
async def list_projects() -> list[dict]:
    return store.list_projects()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate) -> dict:
    return store.create_project(payload.name, payload.brief, payload.client)


@router.get("/{project_id}")
async def get_project(project_id: str) -> dict:
    if project := store.get_project(project_id):
        return project
    raise HTTPException(status_code=404, detail="Project not found")


@router.patch("/{project_id}")
async def update_project(project_id: str, payload: ProjectUpdate) -> dict:
    project = store.update_project(project_id, payload.model_dump(exclude_none=True))
    if project:
        return project
    raise HTTPException(status_code=404, detail="Project not found")
