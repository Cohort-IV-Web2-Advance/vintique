from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status

from app.models.user import User, Account
from app.schemas.user import AccountResponse


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_account(self, user_id: int) -> Optional[Account]:
        return self.db.query(Account).filter(Account.user_id == user_id).first()

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    def update_account_balance(self, user_id: int, new_balance: int) -> Account:
        account = self.db.query(Account).filter(Account.user_id == user_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        account.balance = new_balance
        self.db.commit()
        self.db.refresh(account)
        return account
