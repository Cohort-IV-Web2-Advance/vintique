from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from decimal import Decimal

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

    def update_account_balance(self, user_id: int, new_balance: Decimal) -> Account:
        """
        Update account balance with proper decimal handling.
        
        Args:
            user_id: ID of the user
            new_balance: New balance as Decimal
            
        Returns:
            Account: Updated account object
            
        Raises:
            HTTPException: If account not found
        """
        account = self.db.query(Account).filter(Account.user_id == user_id).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found"
            )
        
        # Ensure new_balance is a Decimal
        if not isinstance(new_balance, Decimal):
            new_balance = Decimal(str(new_balance))
        
        account.balance = new_balance
        self.db.commit()
        self.db.refresh(account)
        return account

    def fund_account(self, user_id: int, amount: Decimal) -> Account:
        """
        Fund account with transactional safety.
        
        Args:
            user_id: ID of the user
            amount: Amount to add (must be positive)
            
        Returns:
            Account: Updated account object
            
        Raises:
            HTTPException: If account not found or amount is invalid
        """
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )
        
        try:
            # Get account and lock for update
            account = self.db.query(Account).filter(Account.user_id == user_id).with_for_update().first()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            
            # Ensure amount is Decimal
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            
            # Update balance
            old_balance = account.balance
            account.balance += amount
            
            self.db.commit()
            self.db.refresh(account)
            
            return account
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fund account: {str(e)}"
            )

    def withdraw_from_account(self, user_id: int, amount: Decimal) -> Account:
        """
        Withdraw from account with sufficient funds check.
        
        Args:
            user_id: ID of the user
            amount: Amount to withdraw (must be positive)
            
        Returns:
            Account: Updated account object
            
        Raises:
            HTTPException: If account not found, insufficient funds, or amount is invalid
        """
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )
        
        try:
            # Get account and lock for update
            account = self.db.query(Account).filter(Account.user_id == user_id).with_for_update().first()
            if not account:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Account not found"
                )
            
            # Ensure amount is Decimal
            if not isinstance(amount, Decimal):
                amount = Decimal(str(amount))
            
            # Check sufficient funds
            if account.balance < amount:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Insufficient funds"
                )
            
            # Update balance
            old_balance = account.balance
            account.balance -= amount
            
            self.db.commit()
            self.db.refresh(account)
            
            return account
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to withdraw from account: {str(e)}"
            )
