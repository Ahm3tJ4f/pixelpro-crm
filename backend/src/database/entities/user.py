from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID

from src.core.enums import UserRole
from src.database.core import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLAlchemyEnum(UserRole, name="user_role"), nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
