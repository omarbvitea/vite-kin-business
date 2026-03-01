from enum import Enum
from datetime import datetime, date
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, Column, String, DateTime, text
from pydantic import EmailStr

class UserRole(str, Enum):
    CREATOR = "CREATOR"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"

class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"

class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"

# User <-> Group Link
class FamilyGroupMember(SQLModel, table=True):
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    family_group_id: Optional[int] = Field(default=None, foreign_key="familygroup.id", primary_key=True)
    role: UserRole = Field(default=UserRole.MEMBER)

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    full_name: Optional[str] = None
    is_active: bool = True

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    
    # Relationships
    groups: List["FamilyGroup"] = Relationship(back_populates="users", link_model=FamilyGroupMember)
    comments: List["Comment"] = Relationship(back_populates="user")
    created_groups: List["FamilyGroup"] = Relationship(back_populates="creator")

class FamilyGroupBase(SQLModel):
    name: str
    description: Optional[str] = None

class FamilyGroup(FamilyGroupBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by_id: int = Field(foreign_key="user.id")
    
    # Relationships
    creator: User = Relationship(back_populates="created_groups")
    users: List[User] = Relationship(back_populates="groups", link_model=FamilyGroupMember)
    tree_members: List["FamilyTreeMember"] = Relationship(back_populates="group")
    invitations: List["Invitation"] = Relationship(back_populates="group")

class FamilyTreeMemberBase(SQLModel):
    first_name: str
    last_name: str
    birth_date: date
    death_date: Optional[date] = None
    photo_url: Optional[str] = None
    biography: Optional[str] = None
    gender: Gender

class FamilyTreeMember(FamilyTreeMemberBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    family_group_id: int = Field(foreign_key="familygroup.id")
    
    group: FamilyGroup = Relationship(back_populates="tree_members")
    comments: List["Comment"] = Relationship(back_populates="tree_member")
    
    # Parent-Child Relationships
    parents: List["ParentChildRelationship"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "FamilyTreeMember.id == ParentChildRelationship.child_id",
            "back_populates": "child"
        }
    )
    children: List["ParentChildRelationship"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "FamilyTreeMember.id == ParentChildRelationship.parent_id",
            "back_populates": "parent"
        }
    )
    
    # Partner Relationships (Symetrical handled via two records or custom logic)
    partners: List["PartnerRelationship"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "FamilyTreeMember.id == PartnerRelationship.member1_id",
            "back_populates": "member1"
        }
    )

class ParentChildRelationship(SQLModel, table=True):
    parent_id: int = Field(foreign_key="familytreemember.id", primary_key=True)
    child_id: int = Field(foreign_key="familytreemember.id", primary_key=True)
    
    parent: "FamilyTreeMember" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "ParentChildRelationship.parent_id == FamilyTreeMember.id"}
    )
    child: "FamilyTreeMember" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "ParentChildRelationship.child_id == FamilyTreeMember.id"}
    )

class PartnerRelationship(SQLModel, table=True):
    member1_id: int = Field(foreign_key="familytreemember.id", primary_key=True)
    member2_id: int = Field(foreign_key="familytreemember.id", primary_key=True)
    relationship_type: str = Field(default="PARTNER") # MARRIED, PARTNER, etc
    
    member1: "FamilyTreeMember" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "PartnerRelationship.member1_id == FamilyTreeMember.id"}
    )
    member2: "FamilyTreeMember" = Relationship(
        sa_relationship_kwargs={"primaryjoin": "PartnerRelationship.member2_id == FamilyTreeMember.id"}
    )

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(foreign_key="user.id")
    tree_member_id: int = Field(foreign_key="familytreemember.id")
    
    user: User = Relationship(back_populates="comments")
    tree_member: FamilyTreeMember = Relationship(back_populates="comments")

class Invitation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr
    token: str = Field(unique=True)
    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
    family_group_id: int = Field(foreign_key="familygroup.id")
    role: UserRole = Field(default=UserRole.MEMBER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    group: FamilyGroup = Relationship(back_populates="invitations")
