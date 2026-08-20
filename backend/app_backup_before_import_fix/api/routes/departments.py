from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.department import Department
from backend.app.models.user import User
from backend.app.schemas.department import DepartmentCreate, DepartmentRead
from backend.app.core.security import get_current_user

router = APIRouter(
    prefix="/departments",
    tags=["departments"],
)


@router.get(
    "/",
    response_model=list[DepartmentRead],
)
def list_departments(
    db: Session = Depends(get_db),
):
    return db.query(Department).all()


@router.post(
    "/",
    response_model=DepartmentRead,
)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(Department)
        .filter(Department.name == department_data.name)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Department already exists",
        )

    department = Department(
        name=department_data.name,
        description=department_data.description,
    )

    db.add(department)
    db.commit()
    db.refresh(department)

    return department


@router.get(
    "/{department_id}",
    response_model=DepartmentRead,
)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
):
    department = (
        db.query(Department)
        .filter(Department.id == department_id)
        .first()
    )

    if department is None:
        raise HTTPException(
            status_code=404,
            detail="Department not found",
        )

    return department
