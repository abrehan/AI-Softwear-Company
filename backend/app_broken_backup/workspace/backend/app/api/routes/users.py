from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.security import get_current_user
from backend.app.models.users import User, UserCreate

router = APIRouter()

class UserSchema(BaseModel):
    username: str
    email: str
    password: str

@router.post("/users/", response_model=User)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, email=user.email)
    db_user.set_password(user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/", response_model=List[User])
def read_users(skip: int = 0, limit: int = 10, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/users/me/", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/users/me/", response_model=User)
def update_users_me(user: UserSchema, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.username:
        current_user.username = user.username
    if user.email:
        current_user.email = user.email
    if user.password:
        current_user.set_password(user.password)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/users/me/", status_code=status.HTTP_204_NO_CONTENT)
def delete_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return {"detail": "User deleted"}