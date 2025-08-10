from enum import Enum


class RedisKeys(str, Enum):
    REFRESH_TOKEN = "refresh_token"
    USER_SESSION = "user_session"
    CITIZEN = "citizen"
    MEETING = "meeting"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


class MeetingStatus(str, Enum):
    CREATED = "CREATED"
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    FINISHED = "FINISHED"
    CANCELLED = "CANCELLED"
