from fastapi import APIRouter
from pydantic import BaseModel
from app.orchestrator.company import Company

router = APIRouter(prefix="/company", tags=["Company"])

company = Company()


class ProjectRequest(BaseModel):
    task: str


@router.post("/build")
async def build_project(request: ProjectRequest):
    return await company.execute_project(request.task)