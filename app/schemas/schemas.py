from typing import List, Optional, Generic, TypeVar
from pydantic import BaseModel, EmailStr
from app.models.models import UserRole, InvitationStatus, Gender
from datetime import datetime, date

# Generic Schema for Response
T = TypeVar("T")

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class FamilyGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None

class FamilyGroupRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    created_by_id: int

class FamilyTreeMemberCreate(BaseModel):
    first_name: str
    last_name: str
    birth_date: date
    death_date: Optional[date] = None
    photo_url: Optional[str] = None
    biography: Optional[str] = None
    gender: Gender

class FamilyTreeMemberRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    birth_date: date
    death_date: Optional[date] = None
    photo_url: Optional[str] = None
    biography: Optional[str] = None
    gender: Gender
    family_group_id: int

class ParentChildCreate(BaseModel):
    parent_id: int
    child_id: int

class PartnerCreate(BaseModel):
    member2_id: int
    relationship_type: str = "PARTNER"

class CommentCreate(BaseModel):
    content: str

class CommentRead(BaseModel):
    id: int
    content: str
    created_at: datetime
    user_id: int
    tree_member_id: int

class InvitationCreate(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.MEMBER

class InvitationRead(BaseModel):
    id: int
    email: EmailStr
    token: str
    status: InvitationStatus
    family_group_id: int
    role: UserRole
    created_at: datetime

class GroupMemberUpdate(BaseModel):
    role: UserRole

class Response(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
