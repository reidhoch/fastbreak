from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class MiscStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Miscellaneous statistics for a player or team in a game."""

    minutes: str
    pointsOffTurnovers: int
    pointsSecondChance: int
    pointsFastBreak: int
    pointsPaint: int
    oppPointsOffTurnovers: int
    oppPointsSecondChance: int
    oppPointsFastBreak: int
    oppPointsPaint: int
    blocks: int
    blocksAgainst: int
    foulsPersonal: int
    foulsDrawn: int
