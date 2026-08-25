from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import authenticate_user, create_access_token, get_current_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRead
from app.database import get_db

router = APIRouter()

@router.post("/login", response_model=UserRead)
async def login(
    user_credentials: UserCreate,
    db: Session = Depends(get_db),
):
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserRead)
async def read_user_me(current_user: User = Depends(get_current_user)):
    return current_user