from datetime import datetime, timedelta, timezone
from typing import Annotated, List

from fastapi import Depends
from pydantic import TypeAdapter

from src.core.utils.jitsi import generate_jitsi_token, JitsiUser
from src.database.entities.citizen import Citizen
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

    def get_meetings(self, operator: User) -> List[MeetingResponse]:
        meetings_with_citizens = (
            self.db.query(Meeting, Citizen)
            .join(Citizen, Meeting.citizen_id == Citizen.id)
            .filter(Meeting.operator_id == operator.id)
            .all()
        )

        meetings_raw_data = [
            {
                "id": meeting.id,
                "status": meeting.status,
                "scheduled_at": meeting.scheduled_at,
                "first_name": citizen.first_name,
                "last_name": citizen.last_name,
                "patronymic": citizen.patronymic,
                "pin_code": citizen.pin_code,
                "phone": citizen.phone,
            }
            for meeting, citizen in meetings_with_citizens
        ]

        ta = TypeAdapter(List[MeetingResponse])
        return ta.validate_python(meetings_raw_data)

    def create_meeting(
        self, request: MeetingRequest, operator: User
    ) -> MeetingResponse:

        citizen_redis_json = get_redis_value(
            self.redis_client, RedisKeys.CITIZEN, request.citizen_pin_code.lower()
        )

        if not citizen_redis_json:
            raise CitizenNotFoundError()

        citizen_redis = CitizenDomain.model_validate_json(citizen_redis_json)

        citizen_db = (
            self.db.query(Citizen)
            .filter(Citizen.pin_code == citizen_redis.pin_code)
            .first()
        )

        if not citizen_db:
            citizen = Citizen(
                first_name=citizen_redis.first_name,
                last_name=citizen_redis.last_name,
                patronymic=citizen_redis.patronymic,
                pin_code=citizen_redis.pin_code,
                phone=request.citizen_phone,
            )
            self.db.add(citizen)
            self.db.commit()
            self.db.refresh(citizen)
            citizen_db = citizen

        meeting = (
            self.db.query(Meeting)
            .filter(Meeting.citizen_id == citizen_db.id)
            .filter(
                Meeting.status.notin_([MeetingStatus.FINISHED, MeetingStatus.CANCELLED])
            )
            .first()
        )

        if meeting:
            raise MeetingAlreadyScheduledError()

        new_meeting = Meeting(
            operator_id=operator.id,
            citizen_id=citizen_db.id,
            scheduled_at=request.scheduled_at,
        )

        self.db.add(new_meeting)
        self.db.commit()
        self.db.refresh(new_meeting)

        otp = generate_otp()

        meeting_redis = MeetingRedisData(otp=otp, citizen_data=citizen_redis)

        meeting_expire_seconds = int(
            (
                request.scheduled_at + timedelta(hours=1) - datetime.now(timezone.utc)
            ).total_seconds()
        )

        set_redis_value(
            self.redis_client,
            RedisKeys.MEETING,
            str(new_meeting.id),
            meeting_redis.model_dump_json(),
            meeting_expire_seconds,
        )

        return MeetingResponse(
            id=new_meeting.id,
            status=new_meeting.status,
            scheduled_at=new_meeting.scheduled_at,
            first_name=citizen_db.first_name,
            last_name=citizen_db.last_name,
            patronymic=citizen_db.patronymic,
            pin_code=citizen_db.pin_code,
            phone=citizen_db.phone,
        )

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

        meeting_redis_json = get_redis_value(
            self.redis_client, RedisKeys.MEETING, str(meeting_id)
        )

        if not meeting_redis_json:
            raise MeetingNotFoundError()

        meeting_redis = MeetingRedisData.model_validate_json(meeting_redis_json)

        if meeting_redis.otp != request.otp:
            raise InvalidOTPError()

        self.join_meeting(meeting_id)

        jitsi_token_payload: JitsiUser = {
            "moderator": False,
            "name": f"{meeting_redis.citizen_data.first_name} {meeting_redis.citizen_data.last_name}",
            "username": meeting_redis.citizen_data.pin_code,
        }

        jitsi_token = generate_jitsi_token(str(meeting_id), jitsi_token_payload)

        return JoinMeetingResponse(jitsi_token=jitsi_token)

    def join_meeting_operator(
        self, meeting_id: MeetingIdPath, operator: User
    ) -> JoinMeetingResponse:

        self.join_meeting(meeting_id)

        jitsi_token_payload: JitsiUser = {
            "moderator": True,
            "name": f"{operator.first_name} {operator.last_name}",
            "username": operator.username,
        }

        jitsi_token = generate_jitsi_token(str(meeting_id), jitsi_token_payload)

        return JoinMeetingResponse(jitsi_token=jitsi_token)

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
