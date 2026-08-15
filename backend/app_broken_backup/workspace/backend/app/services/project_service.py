from fastapi import FastAPI, HTTPException, Depends, APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from sqlalchemy.orm import Session
from db.database import get_db
from models.project import Project as ProjectModel
from schemas.project import ProjectCreate, ProjectUpdate

app = FastAPI()
router = APIRouter()

class Project(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

@router.post("/projects/", response_model=Project)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    project_obj = ProjectModel(**project.dict())
    db.add(project_obj)
    db.commit()
    db.refresh(project_obj)
    return project_obj

@router.get("/projects/", response_model=List[Project])
def read_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    projects = db.query(ProjectModel).offset(skip).limit(limit).all()
    return projects

@router.get("/projects/{project_id}", response_model=Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/projects/{project_id}", response_model=Project)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    project_to_update = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project_to_update:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict(exclude_unset=True).items():
        setattr(project_to_update, key, value)
    db.commit()
    db.refresh(project_to_update)
    return project_to_update

@router.delete("/projects/{project_id}", response_model=Project)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project_to_delete = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project_to_delete:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project_to_delete)
    db.commit()
    return project_to_delete