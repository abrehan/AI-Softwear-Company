from fastapi import APIRouter
from app.agents.agent_registry import registry

router = APIRouter(prefix="/api/registry", tags=["Registry"])


@router.get("/")
async def list_agents():

    return {
        "agents": registry.list_agents()
    }