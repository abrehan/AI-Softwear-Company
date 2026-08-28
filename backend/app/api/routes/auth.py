from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.persistence import store

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=12, max_length=256)
    organization_name: str = Field(min_length=2, max_length=120)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=256)


def bearer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    return authorization.removeprefix("Bearer ")


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest) -> dict:
    user = store.register_user(payload.email, payload.name, payload.password, payload.organization_name)
    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    return {"token": store.create_session(user["id"]), "user": user}


@router.post("/login")
async def login(payload: LoginRequest) -> dict:
    user = store.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return {"token": store.create_session(user["id"]), "user": user}


@router.get("/me")
async def me(authorization: str | None = Header(default=None)) -> dict:
    user = store.get_session_user(bearer_token(authorization))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session is invalid or expired")
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(authorization: str | None = Header(default=None)) -> None:
    store.revoke_session(bearer_token(authorization))
