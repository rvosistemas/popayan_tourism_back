from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from uuid import UUID
from datetime import date


class UserSchema(BaseModel):
    id: Optional[UUID]
    username: constr(min_length=1, max_length=150)
    email: EmailStr
    phone_number: Optional[constr(max_length=20)]
    date_of_birth: Optional[date]

    class Config:
        from_attributes = True


class UserProfileSchema(BaseModel):
    id: Optional[UUID]
    user: UserSchema
    preferences: Optional[dict] = {}
    activity_history: Optional[list] = []

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    username: constr(min_length=1, max_length=150)
    password: constr(min_length=1, max_length=128)

    class Config:
        from_attributes = True


class UserRegisterSchema(BaseModel):
    username: constr(min_length=1, max_length=150)
    email: EmailStr
    password: constr(min_length=1, max_length=128)
    date_of_birth: Optional[date]

    class Config:
        from_attributes = True


class PasswordResetRequestSchema(BaseModel):
    email: EmailStr


class PasswordResetResponseSchema(BaseModel):
    message: str


class PasswordResetSuccessSchema(BaseModel):
    message: str


class PasswordResetErrorSchema(BaseModel):
    error: str


class PasswordResetSchema(BaseModel):
    new_password: constr(min_length=8, max_length=128)
