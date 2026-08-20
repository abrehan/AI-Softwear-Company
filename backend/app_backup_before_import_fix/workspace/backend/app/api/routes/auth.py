from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.app.api.deps import get_db
from backend.app.schemas.auth import TokenData, UserCreate, UserOut
from backend.app.services.auth import authenticate_user, create_access_token, create_user

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = authenticate_user(db, username=user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_user = create_user(db, user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@router.post("/login", response_model=TokenData)
async def login_user(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username=username, password=password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users", response_model=List[UserOut])
async def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users