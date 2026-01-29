from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class MiscStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Miscellaneous statistics for a player or team in a game."""

    minutes: str
    pointsOffTurnovers: int = Field(ge=0)
    pointsSecondChance: int = Field(ge=0)
    pointsFastBreak: int = Field(ge=0)
    pointsPaint: int = Field(ge=0)
    oppPointsOffTurnovers: int = Field(ge=0)
    oppPointsSecondChance: int = Field(ge=0)
    oppPointsFastBreak: int = Field(ge=0)
    oppPointsPaint: int = Field(ge=0)
    blocks: int = Field(ge=0)
    blocksAgainst: int = Field(ge=0)
    foulsPersonal: int = Field(ge=0)
    foulsDrawn: int = Field(ge=0)
