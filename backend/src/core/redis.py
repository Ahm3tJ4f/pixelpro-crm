from typing import Annotated
from fastapi import Depends
from redis import Redis, ConnectionPool
from src.core.constants import REDIS_URL
from src.core.enums import RedisKeys

pool = ConnectionPool.from_url(REDIS_URL, decode_responses=True, max_connections=20)


def get_redis():
    return Redis(connection_pool=pool)


RedisClient = Annotated[Redis, Depends(get_redis)]


def get_redis_value(
    redis_client: RedisClient, namespace: RedisKeys, key: str
) -> str | None:
    return redis_client.get(f"{namespace.value}:{key}") if redis_client else None


def set_redis_value(
    redis_client: RedisClient, namespace: RedisKeys, key: str, value: str, expire: int
) -> bool:
    return (
        redis_client.set(f"{namespace.value}:{key}", value, ex=expire)
        if redis_client
        else False
    )


def delete_redis_value(
    redis_client: RedisClient, namespace: RedisKeys, key: str
) -> bool:
    return redis_client.delete(f"{namespace.value}:{key}") if redis_client else False
