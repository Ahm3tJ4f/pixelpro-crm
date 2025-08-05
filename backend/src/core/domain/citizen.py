# src/core/domain/citizen.py
from datetime import datetime
from pydantic import BaseModel, Field

class CitizenDomain(BaseModel):
    pin_code: str = Field(pattern=r"^[A-HJ-NP-Za-hj-np-z0-9]{7}$")
    first_name: str
    last_name: str
    patronymic: str
    document_number: str = Field(pattern=r"^(AA\d{7}|AZE\d{8})$")
    address_line: str
    date_of_birth: datetime
