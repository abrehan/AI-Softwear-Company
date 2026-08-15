# backend/app/core/config.py

from fastapi import FastAPI
from fastapi.responses import HTTPException
import os
import sys

app = FastAPI()

# Ensure the necessary environment variables are defined
if not os.getenv('DATABASE_URL'):
    raise HTTPException(status_code=401, detail="Database URL is not provided")
if not os.getenv('AUTH_TOKEN'):
    raise HTTPException(status_code=401, detail="Authentication token is not provided")

# Database connection parameters
DATABASE_URL = os.getenv('DATABASE_URL')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')

@app.get('/login', response_model=dict)
async def login():
    # Implement login logic here
    return {'message': 'Login successful'}

if __name__ == '__main__':
    print("Application is running on port 5000")
    app.run(host='127.0.0.1')