from fastapi import APIRouter, Response
from starlette.status import HTTP_204_NO_CONTENT

from src.modules.auth.service import AuthServiceDep, Oauth2Token
from src.modules.auth.model import LoginRequest, AuthResponse, RefreshRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, auth_service: AuthServiceDep):
    return auth_service.login_user(request)


@router.post("/register", response_model=AuthResponse)
def register(request: RegisterRequest, auth_service: AuthServiceDep):
    return auth_service.register_user(request)


@router.post("/refresh", response_model=AuthResponse)
def refresh(request: RefreshRequest, auth_service: AuthServiceDep):
    return auth_service.refresh_user_session(request)


@router.post("/logout", status_code=HTTP_204_NO_CONTENT)
def logout(auth_service: AuthServiceDep, access_token: Oauth2Token):
    auth_service.logout_user(access_token)
    return Response(status_code=HTTP_204_NO_CONTENT)
