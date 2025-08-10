from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from src.modules.auth.service import GetOperatorUser
from src.modules.meetings.service import MeetingServiceDep
from src.modules.meetings.model import (
    JoinMeetingCitizenRequest,
    MeetingRequest,
)
from src.modules.meetings.model import MeetingIdPath

router = APIRouter(prefix="/meetings", tags=["Meetings"])


@router.post("/", status_code=HTTP_201_CREATED)
def create_meeting(
    request: MeetingRequest,
    meeting_service: MeetingServiceDep,
    operator: GetOperatorUser,
):
    return meeting_service.create_meeting(request, operator)


@router.post("/{meetingId}/join/operator")
def join_meeting_operator(
    meeting_id: MeetingIdPath,
    meeting_service: MeetingServiceDep,
    operator: GetOperatorUser,
):
    return meeting_service.join_meeting_operator(meeting_id)


@router.post("/{meetingId}/join/citizen")
def join_meeting_citizen(
    meeting_id: MeetingIdPath,
    request: JoinMeetingCitizenRequest,
    meeting_service: MeetingServiceDep,
):
    return meeting_service.join_meeting_citizen(meeting_id, request)


@router.post("/{meetingId}/finish", status_code=HTTP_204_NO_CONTENT)
def finish_meeting(
    meeting_id: MeetingIdPath,
    meeting_service: MeetingServiceDep,
    operator: GetOperatorUser,
):
    return meeting_service.finish_meeting(meeting_id)
