from enum import Enum


class RedisKeys(str, Enum):
    REFRESH_TOKEN = "refresh_token"
    USER_SESSION = "user_session"
    BLACKLIST = "blacklist"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


class MeetingStatus(str, Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    JOINED = "JOINED"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"
