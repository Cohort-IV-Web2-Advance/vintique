from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    reference = Column(String(255), unique=True, nullable=True)   
    amount = Column(Numeric(10, 2), nullable=False)               
    status = Column(String(50), nullable=False)                    
    provider = Column(String(50), nullable=False, default="paystack") 
    paid_at = Column(DateTime(timezone=True), nullable=True)      
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship back to Order
    order = relationship("Order", back_populates="transactions")