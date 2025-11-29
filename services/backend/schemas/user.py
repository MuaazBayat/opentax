from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    """Base User schema with common attributes"""
    name: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user - all fields optional"""
    name: str | None = None
    email: EmailStr | None = None


class UserResponse(UserBase):
    """Schema for user responses from the API"""
    id: int

    model_config = ConfigDict(from_attributes=True)