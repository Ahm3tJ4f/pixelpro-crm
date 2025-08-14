from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from src.core.enums import RedisKeys, UserRole
from src.core.redis import RedisClient, get_redis_value
from src.modules.auth.model import (
    AuthResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
)

from src.database.core import DbSession
from src.database.entities.user import User
from src.core.exceptions import (
    AuthenticationError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

from src.core.utils.auth import (
    delete_session,
    verify_password,
    decode_jwt,
    set_session,
    get_password_hash,
)

BearerToken = Annotated[str, Depends(HTTPBearer())]


class AuthService:

    def __init__(self, db: DbSession, redis_client: RedisClient):
        self.db = db
        self.redis_client = redis_client

    def login_user(self, request: LoginRequest) -> AuthResponse:
        user = self.db.query(User).filter(User.username == request.username).first()
        if not user:
            raise AuthenticationError()

        if not verify_password(request.password, user.password_hash):
            raise AuthenticationError()

        auth_response = set_session(user, self.redis_client)
        user.last_login_at = datetime.now(timezone.utc)
        self.db.commit()
        return auth_response

    def register_user(self, request: RegisterRequest) -> AuthResponse:
        user = self.db.query(User).filter(User.username == request.username).first()
        if user:
            raise UserAlreadyExistsError()

        password_hash = get_password_hash(request.password)
        new_user = User(
            username=request.username,
            password_hash=password_hash,
            first_name=request.first_name,
            last_name=request.last_name,
            role=request.user_role,
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        auth_response = set_session(new_user, self.redis_client)
        return auth_response

    def refresh_user_session(self, request: RefreshRequest) -> AuthResponse:

        user_id = get_redis_value(
            self.redis_client, RedisKeys.REFRESH_TOKEN, request.refresh_token
        )

        if not user_id:
            raise AuthenticationError()

        user = self.db.query(User).filter(User.id == UUID(user_id)).first()
        if not user:
            raise UserNotFoundError()

        auth_response = set_session(user, self.redis_client)
        return auth_response

    def logout_user(self, bearer_token: BearerToken) -> bool:
        user_session = decode_jwt(bearer_token.credentials)

        if not user_session:
            raise AuthenticationError()

        user = self.db.query(User).filter(User.id == UUID(user_session["sub"])).first()

        if not user:
            raise UserNotFoundError()

        return delete_session(user.id, self.redis_client)

    def get_current_user(self, bearer_token: BearerToken) -> User:
        token_payload = decode_jwt(bearer_token.credentials)
        user_id = UUID(token_payload["sub"])

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundError()
        return user

    def get_operator_user(self, bearer_token: BearerToken) -> User:
        user = self.get_current_user(bearer_token)
        if user.role != UserRole.OPERATOR:
            raise HTTPException(
                status_code=403, detail="Only operators can access this resource"
            )
        return user

    def get_admin_user(self, bearer_token: BearerToken) -> User:
        user = self.get_current_user(bearer_token)
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403, detail="Only admins can access this resource"
            )
        return user


def get_auth_service(db: DbSession, redis_client: RedisClient) -> AuthService:
    return AuthService(db, redis_client)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_operator_user_dependency(
    auth_service: AuthServiceDep, bearer_token: BearerToken
) -> User:
    return auth_service.get_operator_user(bearer_token)


GetOperatorUser = Annotated[User, Depends(get_operator_user_dependency)]


def get_admin_user_dependency(
    auth_service: AuthServiceDep, bearer_token: BearerToken
) -> User:
    return auth_service.get_admin_user(bearer_token)


GetAdminUser = Annotated[User, Depends(get_admin_user_dependency)]
