from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgentCreate(BaseModel):
    name: str
    role: str
    description: str | None = None
    department_id: int
    model: str | None = None


class AgentRead(BaseModel):
    id: int
    name: str
    role: str
    description: str | None = None
    department_id: int
    model: str | None = None
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
