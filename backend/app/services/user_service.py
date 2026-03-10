from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal

from app.models.user import User, Account, UserStatus


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_account(self, user_id: int) -> Optional[Account]:
        return self.db.query(Account).filter(Account.user_id == user_id).first()

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    def update_account_balance(self, user_id: int, new_balance: Decimal) -> Account:
        account = self.db.query(Account).filter(Account.user_id == user_id).first()
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if not isinstance(new_balance, Decimal):
            new_balance = Decimal(str(new_balance))
        account.balance = new_balance
        self.db.commit()
        self.db.refresh(account)
        return account

    def fund_account(self, user_id: int, amount: Decimal) -> Account:
        if amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than 0")
        try:
            account = self.db.query(Account).filter(Account.user_id == user_id).with_for_update().first()
            if not account:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            account.balance += amount
            self.db.commit()
            self.db.refresh(account)
            return account
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to fund account: {str(e)}")

    def withdraw_from_account(self, user_id: int, amount: Decimal) -> Account:
        if amount <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be greater than 0")
        try:
            account = self.db.query(Account).filter(Account.user_id == user_id).with_for_update().first()
            if not account:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            if account.balance < amount:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient funds")
            account.balance -= amount
            self.db.commit()
            self.db.refresh(account)
            return account
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to withdraw from account: {str(e)}")

    def update_user_status(self, identifier: str, action: str, reason: Optional[str] = None):
        """Update user status: suspend, reactivate, or delete."""
        user = None
        try:
            user_id = int(identifier)
            user = self.db.query(User).filter(User.id == user_id).first()
        except ValueError:
            pass

        if not user:
            user = self.db.query(User).filter(User.username == identifier).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User '{identifier}' not found")

        if action == "suspend":
            if user.status == UserStatus.suspended:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User '{user.username}' is already suspended")
            user.status = UserStatus.suspended

        elif action == "reactivate":
            if user.status == UserStatus.active:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User '{user.username}' is already active")
            user.status = UserStatus.active

        elif action == "delete":
            if user.status == UserStatus.inactive:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"User '{user.username}' is already deleted")
            user.status = UserStatus.inactive

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid action '{action}'. Use: suspend, reactivate, delete")

        self.db.commit()
        self.db.refresh(user)
        return {
            "message": f"User '{user.username}' (ID: {user.id}) {action}d successfully",
            "action": action,
            "user_id": user.id,
            "username": user.username,
            "status": user.status.value,
            "reason": reason
        }
