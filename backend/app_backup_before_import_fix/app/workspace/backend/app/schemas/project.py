from pydantic import BaseModel

class ProjectBase(BaseModel):
    title: str
    description: str

class ProjectCreate(ProjectBase):
    owner_id: int

class ProjectUpdate(ProjectBase):
    pass

class ProjectInDBBase(ProjectBase):
    id: int

    class Config:
        orm_mode = True

class Project(ProjectInDBBase):
    pass
