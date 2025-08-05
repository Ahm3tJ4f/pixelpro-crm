from typing import Annotated

from fastapi import Depends
from src.modules.citizens.asan_service import AsanServiceDep
from src.core.enums import RedisKeys
from src.modules.citizens.model import CitizenResponse
from src.core.redis import RedisClient, get_redis_value, set_redis_value
from src.core.constants import CITIZEN_EXPIRE_SECONDS


class CitizenService:
    def __init__(self, redis_client: RedisClient, asan_service: AsanServiceDep):
        self.redis_client = redis_client
        self.asan_service = asan_service

    async def get_citizen(self, pin_code: str) -> CitizenResponse:
        pin_code = pin_code.lower()

        cached_citizen_json = get_redis_value(
            self.redis_client, RedisKeys.CITIZEN, pin_code
        )

        if cached_citizen_json:
            return CitizenResponse.model_validate_json(cached_citizen_json)

        citizen = await self.asan_service.get_citizen(pin_code)
        citizen_json = citizen.model_dump_json()

        set_redis_value(
            self.redis_client,
            RedisKeys.CITIZEN,
            pin_code,
            citizen_json,
            CITIZEN_EXPIRE_SECONDS,
        )

        return CitizenResponse(**citizen.model_dump())


def get_citizen_service(
    redis_client: RedisClient, asan_service: AsanServiceDep
) -> CitizenService:
    return CitizenService(redis_client, asan_service)


CitizenServiceDep = Annotated[CitizenService, Depends(get_citizen_service)]
