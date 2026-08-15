from fastapi import APIRouter
from pydantic import BaseModel
from app.registry.agent_registry import AgentRegistry

class AgentManager:

    def __init__(self):
        self.registry = AgentRegistry()

    def list_agents(self):
        return self.registry.list()

    async def execute(self, agent_name, task):
        agent_class = self.registry.get(agent_name)

        if not agent_class:
            return f"Agent '{agent_name}' not found."

        print(type(agent_class))
        print(agent_class)
        agent = agent_class()

        return await agent.run(task)
router = APIRouter()

manager = AgentManager()


class AgentRequest(BaseModel):
    agent: str
    task: str


@router.get("/agents/{agent_name}")
async def get_agent(agent_name: str):

    agent_class = manager.registry.get(agent_name)

    if not agent_class:
        return {"error": "Agent not found"}

    agent = agent_class()

    return {
        "name": agent.name,
        "role": agent.role
    }

@router.get("/agents")
async def list_agents():
    return {
        "agents": manager.list_agents()
    }

@router.post("/execute")
async def execute(request: AgentRequest):

    return await manager.execute(
        request.agent,
        request.task
    )
