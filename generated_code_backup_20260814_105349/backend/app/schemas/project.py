from pydantic import BaseModel, Field

class ProjectSchema(BaseModel):
    name: str = Field(description="Name of the project")
    description: str = Field(description="Description of the project")