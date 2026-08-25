from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def get_user(
    db: Session,
    user_id: int | None = None,
    username: str | None = None,
) -> User | None:

    query = db.query(User)

    if user_id is not None:
        return (
            query
            .filter(User.id == user_id)
            .first()
        )

    if username:
        return (
            query
            .filter(User.username == username)
            .first()
        )

    return None


def create_user(
    db: Session,
    user: UserCreate,
) -> User:

    existing = (
        db.query(User)
        .filter(
            (User.username == user.username)
            | (User.email == user.email)
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    db_user = User(
        username=user.username,
        email=str(user.email),
        hashed_password=user.password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def update_user(
    db: Session,
    user_id: int,
    user_data,
) -> User:

    db_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if hasattr(user_data, "username") and user_data.username:
        db_user.username = user_data.username

    if hasattr(user_data, "email") and user_data.email:
        db_user.email = str(user_data.email)

    if hasattr(user_data, "disabled") and user_data.disabled is not None:
        db_user.disabled = user_data.disabled

    db.commit()
    db.refresh(db_user)

    return db_user


def delete_user(
    db: Session,
    user_id: int,
) -> None:

    db_user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(db_user)
    db.commit()
