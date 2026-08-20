from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DepartmentCreate(BaseModel):
    name: str
    description: str | None = None


class DepartmentRead(BaseModel):
    id: int
    name: str
    description: str | None = None
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
