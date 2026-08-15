from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

# Import database models and repository
from app.db.models import User, UserRepository
from app.db.repositories import UserRepository

router = APIRouter()

@router.post('/register', response_model=User)
async def register_user(user: dict):
    # Check if the user already exists in the database
    existing_user = await UserRepository.find_by_username(user['username'])
    if existing_user:
        raise HTTPException(status_code=400, detail="Username is already taken")
    
    # Create a new user in the database
    new_user = User(username=user['username'], password=user['password'])
    session = Session()
    try:
        await session.add(new_user)
        await session.commit()
    finally:
        session.close()
    return new_user

@router.get('/login', response_model=User)
async def login_user(user: dict):
    # Retrieve user from database
    user = await UserRepository.find_by_username(user['username'])
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Authenticate the user and return user object
    return user

# Example usage in FastAPI
@app.get("/users", response_model=list[User])
async def get_users():
    # Retrieve all users from database
    users = await UserRepository.all()
    return users