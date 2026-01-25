from pydantic import BaseModel


class SummaryPlayer(BaseModel):
    """Player info as it appears in box score summary (minimal stats)."""

    personId: int
    name: str
    nameI: str
    firstName: str
    familyName: str
    jerseyNum: str


class InactivePlayer(BaseModel):
    """Inactive player info in box score summary."""

    personId: int
    firstName: str
    familyName: str
    jerseyNum: str
