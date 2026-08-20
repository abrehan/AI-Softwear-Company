from fastapi import APIRouter

from backend.app.company.ai_company import AICompany
from backend.app.workflow.workflow_engine import WorkflowEngine

router = APIRouter()


@router.post("/workflow")
async def workflow(project: str):

    company = AICompany()

    await company.build_project(project)

    engine = WorkflowEngine()

    completed = await engine.execute(project)

    return {
        "status": "completed",
        "agents": completed
    }
