from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str  # 用户ID
    exp: int  # 过期时间
    type: str  # token类型: access 或 refresh

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    new_password_confirm: str

class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str
