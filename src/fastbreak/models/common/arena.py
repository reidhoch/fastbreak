from pydantic import BaseModel


class Arena(BaseModel):
    arenaId: int
    arenaName: str
    arenaCity: str
    arenaState: str
    arenaCountry: str
    arenaTimezone: str
    arenaStreetAddress: str
    arenaPostalCode: str
