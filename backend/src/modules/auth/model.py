from src.core.enums import UserRole
from src.core.base_model import CamelModel


class AuthResponse(CamelModel):
    access_token: str
    refresh_token: str


class LoginRequest(CamelModel):
    username: str
    password: str


class RefreshRequest(CamelModel):
    refresh_token: str


class RegisterRequest(CamelModel):
    username: str
    password: str
    first_name: str
    last_name: str
    user_role: UserRole
