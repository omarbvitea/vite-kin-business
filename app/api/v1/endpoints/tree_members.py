from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, or_
from app.db.session import get_session
from app.core.deps import get_current_user
from app.models.models import User, FamilyGroup, FamilyGroupMember, UserRole, FamilyTreeMember, ParentChildRelationship, PartnerRelationship, Comment
from app.schemas.schemas import FamilyTreeMemberCreate, FamilyTreeMemberRead, ParentChildCreate, PartnerCreate, CommentCreate, CommentRead

router = APIRouter()

@router.post("/{group_id}/members", response_model=FamilyTreeMemberRead)
def create_tree_member(
    group_id: int,
    member_in: FamilyTreeMemberCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check permissions (only CREATOR or ADMIN can add tree members)
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == group_id
    )
    membership = db.exec(stmt).first()
    if not membership or membership.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only CREATOR or ADMIN can add tree members")

    # Add tree member
    tree_member = FamilyTreeMember(
        **member_in.dict(),
        family_group_id=group_id
    )
    db.add(tree_member)
    db.commit()
    db.refresh(tree_member)
    return tree_member

@router.get("/{group_id}/members", response_model=List[FamilyTreeMemberRead])
def get_tree_members(
    group_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if user is member of the group
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == group_id
    )
    if not db.exec(stmt).first():
        raise HTTPException(status_code=403, detail="Not a member of this group")

    # List tree members
    stmt_members = select(FamilyTreeMember).where(FamilyTreeMember.family_group_id == group_id)
    return db.exec(stmt_members).all()

@router.post("/{group_id}/relationships/parent-child", response_model=ParentChildCreate)
def add_parent_child_relationship(
    group_id: int,
    rel_in: ParentChildCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Permission check (ADMIN or CREATOR)
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == group_id
    )
    membership = db.exec(stmt).first()
    if not membership or membership.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only CREATOR or ADMIN can modify relationships")

    # Check if members belong to the group
    parent = db.get(FamilyTreeMember, rel_in.parent_id)
    child = db.get(FamilyTreeMember, rel_in.child_id)
    if not parent or not child or parent.family_group_id != group_id or child.family_group_id != group_id:
        raise HTTPException(status_code=404, detail="One or more tree members not found in this group")

    # Create relationship
    rel = ParentChildRelationship(parent_id=rel_in.parent_id, child_id=rel_in.child_id)
    db.add(rel)
    db.commit()
    return rel

@router.post("/{group_id}/members/{member_id}/relationships/partners", response_model=PartnerCreate)
def add_partner_relationship(
    group_id: int,
    member_id: int,
    rel_in: PartnerCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Permission check (ADMIN or CREATOR)
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == group_id
    )
    membership = db.exec(stmt).first()
    if not membership or membership.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only CREATOR or ADMIN can modify relationships")

    # Check members
    m1 = db.get(FamilyTreeMember, member_id)
    m2 = db.get(FamilyTreeMember, rel_in.member2_id)
    if not m1 or not m2 or m1.family_group_id != group_id or m2.family_group_id != group_id:
        raise HTTPException(status_code=404, detail="One or more tree members not found in this group")

    # Create relationship record (both directions)
    rel = PartnerRelationship(member1_id=member_id, member2_id=rel_in.member2_id, relationship_type=rel_in.relationship_type)
    rel_inv = PartnerRelationship(member1_id=rel_in.member2_id, member2_id=member_id, relationship_type=rel_in.relationship_type)
    db.add(rel)
    db.add(rel_inv)
    db.commit()
    return rel

@router.post("/{group_id}/members/{member_id}/comments", response_model=CommentRead)
def add_comment(
    group_id: int,
    member_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # User must be a member of the group
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == group_id
    )
    if not db.exec(stmt).first():
        raise HTTPException(status_code=403, detail="Not a member of this group")

    # Check member
    m = db.get(FamilyTreeMember, member_id)
    if not m or m.family_group_id != group_id:
        raise HTTPException(status_code=404, detail="Tree member not found in this group")

    # Add comment
    comment = Comment(
        content=comment_in.content,
        user_id=current_user.id,
        tree_member_id=member_id
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.get("/{group_id}/members/{member_id}/comments", response_model=List[CommentRead])
def get_comments(
    group_id: int,
    member_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Check if user is member of the group
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == current_user.id,
        FamilyGroupMember.family_group_id == group_id
    )
    if not db.exec(stmt).first():
        raise HTTPException(status_code=403, detail="Not a member of this group")

    # List comments
    stmt_comments = select(Comment).where(Comment.tree_member_id == member_id)
    return db.exec(stmt_comments).all()
