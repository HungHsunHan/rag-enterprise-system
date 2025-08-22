from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class AdminLogin(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    employee_id: str