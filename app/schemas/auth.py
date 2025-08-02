from pydantic import EmailStr, field_validator
from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: int
    type: str

class LoginRequest(BaseModel):
    username: str
    password: str

# 刷新令牌请求
class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
    new_password_confirm: str

    @field_validator("new_password_confirm")
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("密码不匹配")
        return v

class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    new_password_confirm: str

    @field_validator("new_password_confirm")
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("密码不匹配")
        return v
