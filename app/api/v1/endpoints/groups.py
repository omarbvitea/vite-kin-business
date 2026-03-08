from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.db.session import get_session
from app.core.deps import get_current_user
from app.models.models import User, FamilyGroup, FamilyGroupMember, UserRole, Invitation, InvitationStatus
from app.schemas.schemas import FamilyGroupCreate, FamilyGroupRead, InvitationCreate, InvitationRead, GroupMemberUpdate, Response
import secrets

router = APIRouter()

@router.post("/", response_model=Response[FamilyGroupRead])
def create_group(
    group_in: FamilyGroupCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    group = FamilyGroup(
        name=group_in.name,
        description=group_in.description,
        created_by_id=current_user.id
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    
    # Add creator as a member with CREATOR role
    membership = FamilyGroupMember(
        user_id=current_user.id,
        family_group_id=group.id,
        role=UserRole.CREATOR
    )
    db.add(membership)
    db.commit()
    return Response(success=True, message="Group created successfully", data=group)

@router.get("/", response_model=Response[List[FamilyGroupRead]])
def list_my_groups(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Retrieve all groups where the current user is a member
    stmt = select(FamilyGroup).join(FamilyGroupMember).where(FamilyGroupMember.user_id == current_user.id)
    groups = db.exec(stmt).all()
    return Response(success=True, message="Groups retrieved successfully", data=groups)

@router.post("/{group_id}/invite", response_model=Response[InvitationRead])
def invite_user(
    group_id: int,
    inv_in: InvitationCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check permissions (only CREATOR or ADMIN can invite)
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == group_id
    )
    membership = db.exec(stmt).first()
    if not membership or membership.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to invite")

    # Generate token
    token = secrets.token_urlsafe(32)
    invitation = Invitation(
        email=inv_in.email,
        token=token,
        family_group_id=group_id,
        role=inv_in.role
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    return Response(success=True, message="Invitation created successfully", data=invitation)

@router.post("/join/{token}", response_model=Response[FamilyGroupRead])
def join_group(
    token: str,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    stmt = select(Invitation).where(Invitation.token == token, Invitation.status == InvitationStatus.PENDING)
    invitation = db.exec(stmt).first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invalid or expired invitation")
    
    # Check if email matches
    if invitation.email != current_user.email:
        raise HTTPException(status_code=403, detail="Invitation is for a different user")
    
    # Check if already a member
    exist_stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == invitation.family_group_id
    )
    if db.exec(exist_stmt).first():
        invitation.status = InvitationStatus.ACCEPTED
        db.add(invitation)
        db.commit()
        group = db.get(FamilyGroup, invitation.family_group_id)
        return Response(success=True, message="User already a member", data=group)

    # Add member
    membership = FamilyGroupMember(
        user_id=current_user.id,
        family_group_id=invitation.family_group_id,
        role=invitation.role
    )
    db.add(membership)
    
    # Accept invitation
    invitation.status = InvitationStatus.ACCEPTED
    db.add(invitation)
    
    db.commit()
    group = db.get(FamilyGroup, invitation.family_group_id)
    return Response(success=True, message="Joined group successfully", data=group)

@router.patch("/{group_id}/members/{user_id}", response_model=Response[GroupMemberUpdate])
def update_member_role(
    group_id: int,
    user_id: int,
    role_update: GroupMemberUpdate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Only CREATOR can promote to ADMIN
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == group_id
    )
    membership = db.exec(stmt).first()
    if not membership or membership.role != UserRole.CREATOR:
        raise HTTPException(status_code=403, detail="Only CREATOR can update roles")

    # Update member role
    stmt_member = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == user_id,
        FamilyGroupMember.family_group_id == group_id
    )
    target_member = db.exec(stmt_member).first()
    if not target_member:
        raise HTTPException(status_code=404, detail="Member not found in this group")
    
    target_member.role = role_update.role
    db.add(target_member)
    db.commit()
    db.refresh(target_member)
    return Response(success=True, message="Role updated successfully", data=target_member)
