from pydantic import BaseModel, ConfigDict
from humps import camelize


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=camelize,
        populate_by_name=True, 
        str_strip_whitespace=True
    )
