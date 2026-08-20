from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.crud.project import create_project, get_project, update_project, delete_project, get_projects
from backend.app.schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectList
from backend.app.db.session import get_db

router = APIRouter()

@router.post("/projects/", response_model=Project)
def create_new_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = create_project(db=db, project=project)
    if not db_project:
        raise HTTPException(status_code=400, detail="Project already exists")
    return db_project

@router.get("/projects/{project_id}", response_model=Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = get_project(db=db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@router.put("/projects/{project_id}", response_model=Project)
def update_project_details(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    db_project = get_project(db=db, project_id=project_id)
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    updated_project = update_project(db=db, db_item=db_project, item=project)
    return updated_project

@router.delete("/projects/{project_id}", response_model=Project)
def delete_existing_project(project_id: int, db: Session = Depends(get_db)):
    deleted_project = delete_project(db=db, project_id=project_id)
    if not deleted_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return deleted_project

@router.get("/projects/", response_model=ProjectList)
def get_all_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = get_projects(db=db, skip=skip, limit=limit)
    return {"projects": projects}