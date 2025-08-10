import json
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends

from src.core.enums import MeetingStatus, RedisKeys
from src.core.exceptions import (
    CitizenNotFoundError,
    MeetingAlreadyScheduledError,
    MeetingNotFoundError,
    InvalidOTPError,
)
from src.core.redis import (
    RedisClient,
    delete_redis_value,
    get_redis_value,
    set_redis_value,
)
from src.core.domain.citizen import CitizenDomain
from src.core.utils.auth import generate_otp
from src.database.core import DbSession
from src.database.entities.meeting import Meeting
from src.database.entities.user import User
from src.modules.meetings.model import (
    JoinMeetingCitizenRequest,
    MeetingIdPath,
    JoinMeetingResponse,
    MeetingRequest,
    MeetingResponse,
    MeetingRedisData,
)


class MeetingService:
    def __init__(self, db: DbSession, redis_client: RedisClient):
        self.redis_client = redis_client
        self.db = db

    def create_meeting(
        self, request: MeetingRequest, operator: User
    ) -> MeetingResponse:

        cached_citizen_json = get_redis_value(
            self.redis_client, RedisKeys.CITIZEN, request.citizen_pin_code.lower()
        )

        if not cached_citizen_json:
            raise CitizenNotFoundError()

        meeting = (
            self.db.query(Meeting)
            .filter(Meeting.citizen_pin_code == request.citizen_pin_code)
            .filter(Meeting.status != MeetingStatus.FINISHED)
            .first()
        )

        if meeting:
            raise MeetingAlreadyScheduledError()

        new_meeting = Meeting(
            operator_id=operator.id,
            citizen_pin_code=request.citizen_pin_code,
            citizen_phone=request.citizen_phone,
            scheduled_at=request.scheduled_at,
        )

        self.db.add(new_meeting)
        self.db.commit()
        self.db.refresh(new_meeting)

        otp = generate_otp()

        citizen_data = CitizenDomain.model_validate_json(cached_citizen_json)

        meeting_redis_record = MeetingRedisData(otp=otp, citizen_data=citizen_data)

        meeting_expire_seconds = int(
            (
                request.scheduled_at + timedelta(hours=1) - datetime.now(timezone.utc)
            ).total_seconds()
        )

        set_redis_value(
            self.redis_client,
            RedisKeys.MEETING,
            str(new_meeting.id),
            meeting_redis_record.model_dump_json(),
            meeting_expire_seconds,
        )

        return MeetingResponse(id=new_meeting.id, status=new_meeting.status)

    def join_meeting(self, meeting_id: MeetingIdPath) -> Meeting:
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()

        if not meeting:
            raise MeetingNotFoundError()

        if meeting.status == MeetingStatus.CREATED:
            meeting.status = MeetingStatus.PENDING
            self.db.commit()
            self.db.refresh(meeting)
        elif meeting.status == MeetingStatus.PENDING:
            meeting.status = MeetingStatus.IN_PROGRESS
            self.db.commit()
            self.db.refresh(meeting)
        elif meeting.status in [MeetingStatus.CANCELLED, MeetingStatus.FINISHED]:
            raise MeetingNotFoundError()

        return meeting

    def join_meeting_citizen(
        self, meeting_id: MeetingIdPath, request: JoinMeetingCitizenRequest
    ) -> JoinMeetingResponse:

        meeting_redis_record_json = get_redis_value(
            self.redis_client, RedisKeys.MEETING, str(meeting_id)
        )

        if not meeting_redis_record_json:
            raise MeetingNotFoundError()

        meeting_redis_record = MeetingRedisData.model_validate_json(
            meeting_redis_record_json
        )

        if meeting_redis_record.otp != request.otp:
            raise InvalidOTPError()

        self.join_meeting(meeting_id)

        return JoinMeetingResponse(jitsi_token="dummy-citizen-token")

    def join_meeting_operator(self, meeting_id: MeetingIdPath) -> JoinMeetingResponse:

        self.join_meeting(meeting_id)

        return JoinMeetingResponse(jitsi_token="dummy-operator-token")

    def finish_meeting(self, meeting_id: MeetingIdPath) -> None:
        meeting = self.db.query(Meeting).filter(Meeting.id == meeting_id).first()

        if not meeting:
            raise MeetingNotFoundError()

        meeting.status = MeetingStatus.FINISHED
        self.db.commit()
        self.db.refresh(meeting)

        delete_redis_value(self.redis_client, RedisKeys.MEETING, str(meeting_id))


def get_meeting_service(db: DbSession, redis_client: RedisClient) -> MeetingService:
    return MeetingService(db, redis_client)


MeetingServiceDep = Annotated[MeetingService, Depends(get_meeting_service)]
