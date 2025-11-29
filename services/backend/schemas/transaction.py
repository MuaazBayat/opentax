from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from uuid import UUID
from enum import Enum


class TransactionStatus(str, Enum):
    """Enum for transaction status values"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransactionBase(BaseModel):
    """Base Transaction schema with common attributes"""
    sender: int
    payer: int
    currency: str
    amount: float
    status: TransactionStatus

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        # Validate currency is 3-letter ISO code
        if len(v) != 3 or not v.isalpha():
            raise ValueError('Currency must be a 3-letter ISO code (e.g., USD, EUR)')
        return v.upper()


class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    status: TransactionStatus = TransactionStatus.PENDING


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction - all fields optional"""
    sender: Optional[int] = None
    payer: Optional[int] = None
    currency: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[TransactionStatus] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v) != 3 or not v.isalpha():
                raise ValueError('Currency must be a 3-letter ISO code (e.g., USD, EUR)')
            return v.upper()
        return v


class TransactionResponse(TransactionBase):
    """Schema for transaction responses from the API"""
    id: UUID

    model_config = ConfigDict(from_attributes=True)