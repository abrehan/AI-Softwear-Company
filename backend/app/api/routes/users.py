from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import PasswordChange, UserCreate, UserRead, UserUpdate
from app.core.security import get_current_user, hash_password, require_admin, verify_password


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


def validate_password(password: str) -> None:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")


def get_unique_user(db: Session, username: str, email: str, exclude_id: int | None = None):
    username_query = db.query(User).filter(User.username == username)
    email_query = db.query(User).filter(User.email == email)
    if exclude_id is not None:
        username_query = username_query.filter(User.id != exclude_id)
        email_query = email_query.filter(User.id != exclude_id)
    if username_query.first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if email_query.first():
        raise HTTPException(status_code=400, detail="Email already exists")


@router.post("/register", response_model=UserRead)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    get_unique_user(db, user_data.username, user_data.email)
    validate_password(user_data.password)

    # The first account becomes the initial administrator. Later accounts are users.
    is_first_user = db.query(User).count() == 0
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="admin" if is_first_user else "user",
        disabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return db.query(User).order_by(User.id.asc()).all()


@router.get("/me/", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_my_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    validate_password(password_data.new_password)
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="New password must be different")

    current_user.hashed_password = hash_password(password_data.new_password)
    db.commit()
    return None


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    get_unique_user(db, user_data.username, user_data.email)
    validate_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role="user",
        disabled=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email is not None:
        existing = db.query(User).filter(User.email == user_data.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_data.email

    if user_data.role is not None:
        if user.id == admin.id and user_data.role != "admin":
            raise HTTPException(status_code=400, detail="You cannot remove your own administrator role")
        if user_data.role == "user" and user.role == "admin":
            admin_count = db.query(User).filter(User.role == "admin", User.disabled == False).count()
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="At least one active administrator is required")
        user.role = user_data.role

    if user_data.disabled is not None:
        if user.id == admin.id and user_data.disabled:
            raise HTTPException(status_code=400, detail="You cannot disable your own account")
        if user_data.disabled and user.role == "admin":
            admin_count = db.query(User).filter(User.role == "admin", User.disabled == False).count()
            if admin_count <= 1:
                raise HTTPException(status_code=400, detail="At least one active administrator is required")
        user.disabled = user_data.disabled

    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")
    if user.role == "admin":
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="At least one administrator is required")

    db.delete(user)
    db.commit()
    return None
