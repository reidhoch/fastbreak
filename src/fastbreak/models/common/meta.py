from pydantic import BaseModel


class Meta(BaseModel):
    version: int
    request: str
    time: str
