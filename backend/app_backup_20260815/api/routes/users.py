from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserRead
from backend.app.core.security import (
    get_current_user,
    hash_password,
)


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post(
    "/register",
    response_model=UserRead,
)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):

    existing = (
        db.query(User)
        .filter(
            User.username == user_data.username
        )
        .first()
    )

    if existing:

        raise HTTPException(
            status_code=400,
            detail="Username already exists",
        )

    existing_email = (
        db.query(User)
        .filter(
            User.email == user_data.email
        )
        .first()
    )

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(
            user_data.password
        ),
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


@router.get(
    "/",
    response_model=list[UserRead],
)
def list_users(
    db: Session = Depends(get_db),
):

    return db.query(User).all()


@router.get(
    "/me/",
    response_model=UserRead,
)
def read_users_me(
    current_user: User = Depends(
        get_current_user
    ),
):

    return current_user
