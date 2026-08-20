from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class UserInDB(User):
    hashed_password: str

fake_users_db = {
    1: UserInDB(id=1, username="johndoe", email="john@example.com", hashed_password="$2b$12$EixZaYVK1fsbwBQNqF0bevQwLsAiXpl8JxTZeUgXVFnCubpkoS5k8", is_active=True),
    2: UserInDB(id=2, username="jane", email="jane@example.com", hashed_password="$2b$12$K4WXaYVK1fsbwBQNqF0bevQwLsAiXpl8JxTZeUgXVFnCubpkoS5k8", is_active=False)
}

def get_user(db, user_id: int):
    if user_id in db:
        return db[user_id]
    else:
        raise HTTPException(status_code=404, detail="User not found")

@router.get("/users/", response_model=List[User])
async def read_users():
    users = fake_users_db.values()
    return list(users)

@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int):
    user = get_user(fake_users_db, user_id=user_id)
    return user

@router.post("/users/", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user: User):
    fake_users_db[user.id] = UserInDB(**user.dict(), hashed_password="hashed_password")
    return fake_users_db[user.id]

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: User):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    fake_users_db[user_id] = UserInDB(**user.dict(), hashed_password="hashed_password")
    return fake_users_db[user_id]

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    if user_id not in fake_users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del fake_users_db[user_id]