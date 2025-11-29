from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


class InvoiceBase(BaseModel):
    """Base Invoice schema with common attributes"""
    sender: int
    payer: int
    amount: float
    lineItems: str

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Amount must be positive')
        return v


class InvoiceCreate(InvoiceBase):
    """Schema for creating a new invoice"""
    pass


class InvoiceUpdate(BaseModel):
    """Schema for updating an invoice - all fields optional"""
    sender: Optional[int] = None
    payer: Optional[int] = None
    amount: Optional[float] = None
    lineItems: Optional[str] = None

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return v


class InvoiceResponse(InvoiceBase):
    """Schema for invoice responses from the API"""
    id: int

    model_config = ConfigDict(from_attributes=True)