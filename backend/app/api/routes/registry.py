from fastapi import APIRouter

from app.registry.agent_registry import registry

router = APIRouter(
    prefix="/api/registry",
    tags=["Registry"],
)


@router.get("/")
async def list_agents():
    return {
        "agents": registry.list()
    }


@router.get("/{agent_key}")
async def get_agent(agent_key: str):

    try:
        agent_class = registry.get(agent_key)
    except ValueError:
        return {
            "error": f"Agent '{agent_key}' not found"
        }

    agent = agent_class()

    return {
        "key": agent_key,
        "name": agent.name,
        "role": agent.role,
        "model": agent.model,
    }


