from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional

class AnalyzeRequest(BaseModel):
    user_prompt: str = Field(..., min_length=1, description="The message from the user")

class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)

class UserResponse(UserBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None