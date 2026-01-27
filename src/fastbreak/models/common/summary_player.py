from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class SummaryPlayer(PandasMixin, PolarsMixin, BaseModel):
    """Player info as it appears in box score summary (minimal stats)."""

    personId: int
    name: str
    nameI: str
    firstName: str
    familyName: str
    jerseyNum: str


class InactivePlayer(PandasMixin, PolarsMixin, BaseModel):
    """Inactive player info in box score summary."""

    personId: int
    firstName: str
    familyName: str
    jerseyNum: str
