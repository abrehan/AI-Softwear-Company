from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")

class UserUpdate(BaseModel):
    email: EmailStr = Field(None, description="User's email address")
    password: str = Field(None, description="User's password")
    first_name: str = Field(None, description="User's first name")
    last_name: str = Field(None, description="User's last name")

class UserRead(BaseModel):
    id: int = Field(..., description="User's ID")
    email: EmailStr = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")