from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from app.persistence import store

router = APIRouter(prefix="/tasks", tags=["Tasks"])
VALID_STATUSES = {"backlog", "ready", "in_progress", "review", "done"}


class TaskCreate(BaseModel):
    title: str = Field(min_length=2, max_length=240)
    project_id: str | None = None
    owner: str | None = Field(default=None, max_length=80)
    department: str = Field(default="strategy", max_length=80)


class TaskUpdate(BaseModel):
    status: str | None = None
    owner: str | None = Field(default=None, max_length=80)
    title: str | None = Field(default=None, min_length=2, max_length=240)


@router.get("")
async def list_tasks(project_id: str | None = None) -> list[dict]:
    return store.list_tasks(project_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate) -> dict:
    return store.create_task(payload.title, payload.project_id, payload.owner, payload.department)


@router.patch("/{task_id}")
async def update_task(task_id: str, payload: TaskUpdate) -> dict:
    changes = payload.model_dump(exclude_none=True)
    if "status" in changes and changes["status"] not in VALID_STATUSES:
        raise HTTPException(status_code=422, detail=f"Status must be one of: {', '.join(sorted(VALID_STATUSES))}")
    task = store.update_task(task_id, changes)
    if task:
        return task
    raise HTTPException(status_code=404, detail="Task not found")
