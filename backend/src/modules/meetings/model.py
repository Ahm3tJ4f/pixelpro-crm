from datetime import datetime
from uuid import UUID
from typing import Annotated
from fastapi import Path
from pydantic import BaseModel, Field
from src.core.enums import MeetingStatus
from src.core.base_model import CamelModel
from src.core.domain.citizen import CitizenDomain

MeetingIdPath = Annotated[UUID, Path(alias="meetingId")]

class MeetingRequest(CamelModel):
    citizen_pin_code: str = Field(pattern=r"^[A-HJ-NP-Za-hj-np-z0-9]{7}$")
    citizen_phone: str = Field(pattern=r"^994\d{9}$")
    scheduled_at: datetime

class MeetingResponse(CamelModel):
    id: UUID
    status: MeetingStatus

class JoinMeetingCitizenRequest(CamelModel):
    otp: str = Field(pattern=r"^[0-9]{6}$")

class JoinMeetingResponse(CamelModel):
    jitsi_token: str

class MeetingRedisData(BaseModel):
    otp: str = Field(pattern=r"^[0-9]{6}$")
    citizen_data: CitizenDomain
