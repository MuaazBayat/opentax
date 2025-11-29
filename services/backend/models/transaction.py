from sqlalchemy import Column, Integer, String, Uuid, Double, ForeignKey, DateTime
from db import Base
import uuid
from datetime import datetime, timezone

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    sender = Column(Integer, ForeignKey("users.id"), index=True)
    receiver = Column(Integer, ForeignKey("users.id"), index=True)
    currency = Column(String)
    amount = Column(Double)
    status = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
