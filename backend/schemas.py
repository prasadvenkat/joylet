from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid
import re

def validate_email(email: str) -> str:
    """Simple email validation"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError('Invalid email format')
    return email

class UserRegister(BaseModel):
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., max_length=40)
    
    @validator('email')
    def validate_email_format(cls, v):
        return validate_email(v)

class UserLogin(BaseModel):
    email: str
    password: str

class EmailVerification(BaseModel):
    token: uuid.UUID

class UserResponse(BaseModel):
    id: uuid.UUID
    display_name: str
    handle: str

class UserProfile(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str
    handle: str
    created_at: datetime

class PublicUserProfile(BaseModel):
    id: uuid.UUID
    display_name: str
    handle: str
    created_at: datetime
    post_count: int

class PostCreate(BaseModel):
    body: str = Field(..., max_length=140)
    parent_id: Optional[uuid.UUID] = None

class PostResponse(BaseModel):
    id: uuid.UUID
    body: str
    author: Optional[UserResponse]
    parent_id: Optional[uuid.UUID]
    like_count: int
    reply_count: int
    user_liked: bool
    created_at: datetime

class PostList(BaseModel):
    items: List[PostResponse]
    next_cursor: Optional[str]

class PostDetail(BaseModel):
    post: PostResponse
    replies: List[PostResponse]

class LikeResponse(BaseModel):
    liked: bool
    like_count: int

class MessageResponse(BaseModel):
    message: str