from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.registry.agent_registry import registry

router = APIRouter(
    prefix="/api/ai-agents",
    tags=["AI Agents"],
)


class AIExecuteRequest(BaseModel):
    agent: str
    task: str


@router.get("/")
async def list_ai_agents():

    return {
        "agents": registry.list()
    }


@router.get("/{agent_key}")
async def get_ai_agent(agent_key: str):

    try:
        agent_class = registry.get(agent_key)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_key}' not found",
        )

    agent = agent_class()

    return {
        "key": agent_key,
        "name": agent.name,
        "role": agent.role,
        "model": agent.model,
    }


@router.post("/execute")
async def execute_ai_agent(request: AIExecuteRequest):

    try:
        agent_class = registry.get(request.agent)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{request.agent}' not found",
        )

    agent = agent_class()

    try:
        result = await agent.run(request.task)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(exc)}",
        )

    return {
        "success": True,
        "agent": request.agent,
        "name": agent.name,
        "role": agent.role,
        "model": agent.model,
        "task": request.task,
        "result": result,
    }
