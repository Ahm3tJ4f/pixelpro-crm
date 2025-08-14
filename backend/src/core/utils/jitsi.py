from datetime import datetime, timezone, timedelta
from typing import TypedDict
from jose import jwt
from src.core.constants import (
    JITSI_JWT_SECRET,
    JITSI_ISSUER,
    JITSI_AUDIENCE,
    JITSI_SUBJECT,
    JITSI_GROUP,
    JITSI_TOKEN_EXPIRY_HOURS,
)


class JitsiUser(TypedDict):
    moderator: bool
    name: str
    username: str


def generate_jitsi_token(
    room_id: str,
    user_data: JitsiUser,
) -> str:

    now = datetime.now(timezone.utc)
    exp_time = now + timedelta(hours=JITSI_TOKEN_EXPIRY_HOURS)

    payload = {
        "context": {
            **user_data,
            "group": JITSI_GROUP,
        },
        "iss": JITSI_ISSUER,
        "aud": JITSI_AUDIENCE,
        "sub": JITSI_SUBJECT,
        "room": room_id,
        "iat": int(now.timestamp()),
        "exp": int(exp_time.timestamp()),
    }

    encoded_jwt = jwt.encode(payload, JITSI_JWT_SECRET, algorithm="HS256")
    return encoded_jwt
