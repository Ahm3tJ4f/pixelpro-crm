from src.core.base_model import CamelModel
from datetime import datetime


class GetUserResponse(CamelModel):
    id: str
    username: str
    first_name: str
    last_name: str
    role: str
    last_login_at: datetime
    created_at: datetime
    updated_at: datetime


class UpdateUserRequest(CamelModel):
    first_name: str
    last_name: str
    patronymic: str
    date_of_birth: datetime
    document_number: str
    address_line: str
    phone_number: str
    email: str
