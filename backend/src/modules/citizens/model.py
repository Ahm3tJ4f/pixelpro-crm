from datetime import datetime
from typing import Annotated
from fastapi import Path
from pydantic import Field
from src.core.base_model import CamelModel

CitizenRequestPath = Annotated[str, Path(pattern=r"^[A-HJ-NP-Za-hj-np-z0-9]{7}$", alias="pinCode")]


class CitizenResponse(CamelModel):
    first_name: str
    last_name: str
    patronymic: str
    pin_code: str = Field(pattern=r"^[A-HJ-NP-Za-hj-np-z0-9]{7}$")
    document_number: str = Field(pattern=r"^(AA\d{7}|AZE\d{8})$")
    address_line: str
    date_of_birth: datetime
