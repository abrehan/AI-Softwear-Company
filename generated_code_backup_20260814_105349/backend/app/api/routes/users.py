# backend/app/api/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, Request, status

router = APIRouter()

@router.post("/register", response_model=User)
async def register_user(
    db: UserDatabase,
    username: str,
    password_hash: str,
    email: str
) -> User:
    user = await db.register(username, password_hash, email)
    return user

@router.get("/")
async def read_users():
    users = await db.read_all()
    return {"users": users}