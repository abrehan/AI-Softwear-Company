from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import sessionmaker
import os

app = FastAPI()

# Database configuration
DATABASE_URL = "sqlite:///virtual_office.db"
engine = sessionmaker(bind=DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@app.post("/projects", response_model=schemas.Project, status_code=201)
async def create_project(project: schemas.ProjectCreate):
    db = SessionLocal()
    try:
        new_project = db.add(project)
        await db.commit()
        return new_project
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}", response_model=schemas.ProjectGet)
async def get_project(project_id: int):
    db = SessionLocal()
    try:
        project = await db.get(Project).filter_by(id=project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/projects/{project_id}")
async def delete_project(project_id: int):
    db = SessionLocal()
    try:
        project = await db.get(Project).filter_by(id=project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        db.delete(project)
        await db.commit()
        return {"message": "Project deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Main route for the API
@app.get("/")
async def read_projects():
    db = SessionLocal()
    try:
        projects = await db.query(Project).all()
        return {"projects": projects}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))