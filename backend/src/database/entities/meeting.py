from datetime import timezone, datetime
from uuid import uuid4
from sqlalchemy import VARCHAR, Column, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
from src.core.enums import MeetingStatus
from src.database.core import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    operator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    citizen_pin_code = Column(VARCHAR(7), nullable=False)
    citizen_phone = Column(VARCHAR(12), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    status = Column(
        SQLAlchemyEnum(MeetingStatus, name="meeting_status"),
        nullable=False,
        default=MeetingStatus.CREATED,
    )
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
