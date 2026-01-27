from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class Arena(PandasMixin, PolarsMixin, BaseModel):
    arenaId: int
    arenaName: str
    arenaCity: str
    arenaState: str
    arenaCountry: str
    arenaTimezone: str
    arenaStreetAddress: str
    arenaPostalCode: str
