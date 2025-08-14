from datetime import timezone, datetime
from uuid import uuid4
from sqlalchemy import VARCHAR, Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from src.database.core import Base


class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False)
    first_name = Column(VARCHAR(255), nullable=False)
    last_name = Column(VARCHAR(255), nullable=False)
    pin_code = Column(VARCHAR(7), nullable=False)
    patronymic = Column(VARCHAR(255), nullable=True)
    phone = Column(VARCHAR(12), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
