import asyncio
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from src.core.exceptions import CitizenNotFoundError
from src.core.domain.citizen import CitizenDomain


class AsanService:
    def __init__(self):
        pass

    async def get_citizen(self, pin_code: str) -> CitizenDomain:

        # dummy sleep
        await asyncio.sleep(1)

        if pin_code != "2dnxyd8":
            raise CitizenNotFoundError()

        return CitizenDomain(
            pin_code="2DNXYD8",
            first_name="Ahmad",
            last_name="Jafarov",
            patronymic="Roman",
            document_number="AA1234567",
            address_line="Azerbaijan, Baku",
            date_of_birth=datetime(2002, 3, 12, tzinfo=timezone.utc),
        )


def get_asan_service() -> AsanService:
    return AsanService()


AsanServiceDep = Annotated[AsanService, Depends(get_asan_service)]
