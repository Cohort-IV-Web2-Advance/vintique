from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta

from app.models.user import User, Account
from app.schemas.user import UserCreate, UserLogin
from app.core.auth import verify_password, get_password_hash, create_access_token
from app.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: UserCreate) -> User:
        # Check if user already exists
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if self.db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            password=hashed_password,
            shipping_address=user_data.shipping_address
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Create account for user
        account = Account(user_id=user.id, balance=0)
        self.db.add(account)
        self.db.commit()

        return user

    def login(self, login_data: UserLogin) -> dict:
        user = self.db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
