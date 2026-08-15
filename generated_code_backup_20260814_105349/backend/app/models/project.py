from fastapi import FastAPI, Request
import json

app = FastAPI()

# Define the schema for Project model
class ProjectSchema:
    id: int
    name: str
    description: str
    owner_id: int
    created_at: str
    updated_at: str

# API endpoint to retrieve all projects
@app.get("/projects")
async def get_projects():
    # Retrieve all projects from the database
    projects = await ProjectSchema.objects.all()
    return {"projects": projects}

# API endpoint to create a new project
@app.post("/projects/")
async def create_project(request: Request):
    data = await request.json()
    new_project = ProjectSchema(**data)
    # Create a new project in the database
    new_project.save()
    return {"message": "Project created successfully", "project": new_project}

# API endpoint to retrieve a specific project by ID
@app.get("/{project_id}")
async def get_project(project_id: int):
    # Retrieve a project from the database
    project = await ProjectSchema.objects.get(id=project_id)
    return {"project": project}