from fastapi import APIRouter
from pydantic import BaseModel

from app.company.ai_company import AICompany


router = APIRouter(
    prefix="/api/company",
    tags=["Company"]
)


class ProjectRequest(BaseModel):
    task: str


@router.post("/build")
async def build(request: ProjectRequest):

    company = AICompany()

    result = await company.build_project(
        request.task
    )

    return {
        "status": "success",
        "agents": list(result.keys())
    }

