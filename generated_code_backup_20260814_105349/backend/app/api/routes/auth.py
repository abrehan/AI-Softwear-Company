from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import BearerAuth
from typing import Optional

app = FastAPI()

# Define the API key for authentication
async def get_api_key(request: Request):
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Authentication token is missing"
        )
    
    # Split the auth header by 'Bearer '
    _, api_key = auth_header.split(' ')
    
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token format"
        )
    
    return api_key

# Define the route for authentication
@app.post("/auth", response_model=dict, dependencies=[Depends(get_api_key)])
async def authenticate(api_key: str):
    # Implement your logic to verify the API key
    if api_key != "secret_token":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return {"message": "Authentication successful"}

# Example route for user registration
@app.post("/users", response_model=dict, dependencies=[Depends(get_api_key)])
async def register_user(api_key: str, username: str, email: str):
    # Implement your logic to register a new user
    if not username or not email:
        raise HTTPException(
            status_code=400,
            detail="Invalid username or email format"
        )
    
    return {"message": "User registered successfully"}