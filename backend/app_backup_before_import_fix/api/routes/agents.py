from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.agent import Agent
from backend.app.models.department import Department
from backend.app.models.user import User
from backend.app.schemas.agent import AgentCreate, AgentRead
from backend.app.core.security import get_current_user


router = APIRouter(
    prefix="/agents",
    tags=["agents"],
)


class AgentExecuteRequest(BaseModel):
    task: str


@router.get(
    "/",
    response_model=list[AgentRead],
)
def list_agents(
    db: Session = Depends(get_db),
):
    return (
        db.query(Agent)
        .order_by(Agent.id)
        .all()
    )


@router.post(
    "/",
    response_model=AgentRead,
)
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    department = (
        db.query(Department)
        .filter(
            Department.id == agent_data.department_id
        )
        .first()
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    agent = Agent(
        name=agent_data.name,
        role=agent_data.role,
        description=agent_data.description,
        department_id=agent_data.department_id,
        model=agent_data.model,
        active=True,
    )

    db.add(agent)
    db.commit()
    db.refresh(agent)

    return agent


@router.get(
    "/{agent_id}",
    response_model=AgentRead,
)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id)
        .first()
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    return agent


@router.delete(
    "/{agent_id}",
)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id)
        .first()
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    db.delete(agent)
    db.commit()

    return {
        "message": "Agent deleted",
        "id": agent_id,
    }


@router.post(
    "/{agent_id}/execute",
)
def execute_agent(
    agent_id: int,
    request: AgentExecuteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    agent = (
        db.query(Agent)
        .filter(Agent.id == agent_id)
        .first()
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found",
        )

    if not agent.active:
        raise HTTPException(
            status_code=400,
            detail="Agent is inactive",
        )

    return {
        "agent_id": agent.id,
        "agent": agent.name,
        "role": agent.role,
        "model": agent.model,
        "task": request.task,
        "status": "accepted",
        "message": "Agent task accepted. AI execution engine will be connected next.",
    }
