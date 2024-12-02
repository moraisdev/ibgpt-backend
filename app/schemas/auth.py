from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    cnpj: str
    company_name: str
    job_title: str


class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    id: int
    name: str
    last_name: str
    email: EmailStr
    phone: str
    cnpj: str
    company_name: str
    job_title: str
    role: RoleResponse
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class LoginForm(BaseModel):
    email: EmailStr
    password: str


class ResetPasswordForm(BaseModel):
    current_password: str
    new_password: str
