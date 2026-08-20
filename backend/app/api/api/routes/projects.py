from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectRead,
)
from app.core.security import get_current_user


router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.get(
    "/",
    response_model=list[ProjectRead],
)
def get_projects(
    db: Session = Depends(get_db),
):

    return db.query(Project).all()


@router.post(
    "/",
    response_model=ProjectRead,
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=current_user.id,
    )

    db.add(project)

    db.commit()

    db.refresh(project)

    return project


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
):

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if project is None:

        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


