from pydantic import BaseModel


class Period(BaseModel):
    period: int
    periodType: str
    score: int
