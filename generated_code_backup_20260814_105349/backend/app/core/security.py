from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, JWTToken
from database.database import SessionLocal
from app.auth_service import get_user_by_email

# Database session configuration
async def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Generate a secure JWT token using OAuth 2.0
async def get_token(request: OAuth2PasswordRequestForm):
    # Authenticate the user
    if not request.username or not request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Retrieve user from database
    user = await get_user_by_email(db, request.username)
    
    # Generate a JWT token
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Return the JWT token
    return JWTToken(access_token=str(user.id))

# Implement OAuth 2.0 strategy for authentication
async def get_auth_strategy(request: OAuth2PasswordRequestForm):
    return {"type": "oauth2", "tokenUrl": f"/login?redirect_uri={request.oauth2_response[1]}"}

# Import dependencies
from fastapi.security import Depends, HTTPException

# Database session configuration
async def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

# Generate a secure JWT token using OAuth 2.0
async def get_token(request: OAuth2PasswordRequestForm):
    # Authenticate the user
    if not request.username or not request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Retrieve user from database
    user = await get_user_by_email(db, request.username)
    
    # Generate a JWT token
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Return the JWT token
    return JWTToken(access_token=str(user.id))

# Implement OAuth 2.0 strategy for authentication
async def get_auth_strategy(request: OAuth2PasswordRequestForm):
    return {"type": "oauth2", "tokenUrl": f"/login?redirect_uri={request.oauth2_response[1]}"}