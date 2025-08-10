import secrets
from datetime import timedelta, datetime, timezone
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.core.enums import RedisKeys
from src.core.redis import (
    get_redis_value,
    set_redis_value,
    delete_redis_value,
    RedisClient,
)
from src.core.constants import (
    REFRESH_TOKEN_EXPIRE_SECONDS,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.core.exceptions import AuthenticationError
from src.core.logging import logger
from src.modules.auth.model import AuthResponse
from src.database.entities.user import User

# Password utilities
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt_context.verify(plain_password, hashed_password)


# Token utilities
def generate_access_token(data: dict) -> str:
    """Generate JWT access token"""
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {str(e)}")
        raise AuthenticationError()


def set_session(user: User, redis_client: RedisClient) -> AuthResponse:
    token_payload = {"sub": str(user.id), "username": user.username, "role": user.role}
    access_token = generate_access_token(token_payload)
    refresh_token = secrets.token_urlsafe(32)

    old_refresh_token = get_redis_value(redis_client, RedisKeys.USER_SESSION, str(user.id))

    if old_refresh_token:
        delete_redis_value(redis_client, RedisKeys.REFRESH_TOKEN, old_refresh_token)

    set_redis_value(
        redis_client,
        RedisKeys.USER_SESSION,
        str(user.id),
        refresh_token,
        REFRESH_TOKEN_EXPIRE_SECONDS,
    )

    set_redis_value(
        redis_client,
        RedisKeys.REFRESH_TOKEN,
        refresh_token,
        str(user.id),
        REFRESH_TOKEN_EXPIRE_SECONDS,
    )

    return AuthResponse(access_token=access_token, refresh_token=refresh_token)


def delete_session(user_id: UUID, redis_client: RedisClient) -> bool:
    """Delete session bidirectionally by user ID"""
    user_id_str = str(user_id)
    refresh_token = get_redis_value(redis_client, RedisKeys.USER_SESSION, user_id_str)

    if not refresh_token:
        return False

    delete_redis_value(redis_client, RedisKeys.REFRESH_TOKEN, refresh_token)
    delete_redis_value(redis_client, RedisKeys.USER_SESSION, user_id_str)

    return True


def generate_otp(length: int = 6) -> str:
    return "".join(str(secrets.randbelow(10)) for _ in range(length))
