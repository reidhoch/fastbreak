from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class TraditionalGroupStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Traditional statistics for a group (starters or bench)."""

    minutes: str
    fieldGoalsMade: int
    fieldGoalsAttempted: int
    fieldGoalsPercentage: float
    threePointersMade: int
    threePointersAttempted: int
    threePointersPercentage: float
    freeThrowsMade: int
    freeThrowsAttempted: int
    freeThrowsPercentage: float
    reboundsOffensive: int
    reboundsDefensive: int
    reboundsTotal: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    foulsPersonal: int
    points: int


class TraditionalStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Traditional box score statistics for a player or team."""

    plusMinusPoints: float
