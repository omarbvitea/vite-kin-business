from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.db.session import get_session
from app.models.models import User
from app.schemas.schemas import UserCreate, UserRead, Token, Response
from app.core.security import create_access_token, get_password_hash, verify_password
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Response[UserRead])
def register(user_in: UserCreate, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.email == user_in.email)).first()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return Response(success=True, message="User registered successfully", data=new_user)

@router.post("/login", response_model=Response[Token])
def login(db: Session = Depends(get_session), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    token_data = {"access_token": access_token, "token_type": "bearer"}
    return Response(success=True, message="Login successful", data=token_data)
