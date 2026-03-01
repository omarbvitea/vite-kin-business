from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel import Session, select
from app.core.config import settings
from app.db.session import get_session
from app.models.models import User, FamilyGroupMember, UserRole
from pydantic import ValidationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user(
    db: Session = Depends(get_session), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception
    
    user = db.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user

# Role-Based Permissions
def check_group_role(group_id: int, roles: List[UserRole]):
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_session)
    ):
        stmt = select(FamilyGroupMember).where(
            FamilyGroupMember.user_id == current_user.id,
            FamilyGroupMember.family_group_id == group_id
        )
        membership = db.exec(stmt).first()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this group"
            )
        if membership.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {[r.value for r in roles]}"
            )
        return membership
    return role_checker

# Helper to check permissions on the fly within routes
def get_user_role_in_group(user_id: int, group_id: int, db: Session) -> Optional[UserRole]:
    stmt = select(FamilyGroupMember).where(
        FamilyGroupMember.user_id == user_id,
        FamilyGroupMember.family_group_id == group_id
    )
    membership = db.exec(stmt).first()
    return membership.role if membership else None
