from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional

class AnalyzeRequest(BaseModel):
    user_prompt: str = Field(..., min_length=1, description="The message from the user")

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(min_length=1, max_length=50)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)

class UserPublic(BaseModel):
    id: int
    username: str
    model_config = ConfigDict(from_attributes=True)

class UserPrivate(UserPublic):
    email: EmailStr

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=1, max_length=50)
    password: str | None = Field(default=None, min_length=8, max_length=72)

class Token(BaseModel):
    access_token: str
    token_type: str