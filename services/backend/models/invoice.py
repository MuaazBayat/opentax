from sqlalchemy import Column, Integer, String, Double, ForeignKey, DateTime
from db import Base
from datetime import datetime, timezone

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(Integer, ForeignKey("users.id"), index=True)
    payer = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Double)
    currency = Column(String, default="USD")
    lineItems = Column(String)
    status = Column(String, default="UNPAID")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))