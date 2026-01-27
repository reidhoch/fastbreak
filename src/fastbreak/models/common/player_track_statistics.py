from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class PlayerTrackStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Player tracking statistics for an individual player."""

    minutes: str
    speed: float
    distance: float
    reboundChancesOffensive: int
    reboundChancesDefensive: int
    reboundChancesTotal: int
    touches: int
    secondaryAssists: int
    freeThrowAssists: int
    passes: int
    assists: int
    contestedFieldGoalsMade: int
    contestedFieldGoalsAttempted: int
    contestedFieldGoalPercentage: float
    uncontestedFieldGoalsMade: int
    uncontestedFieldGoalsAttempted: int
    uncontestedFieldGoalsPercentage: float
    fieldGoalPercentage: float
    defendedAtRimFieldGoalsMade: int
    defendedAtRimFieldGoalsAttempted: int
    defendedAtRimFieldGoalPercentage: float


class TeamPlayerTrackStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Player tracking statistics aggregated at team level."""

    minutes: str
    distance: float
    reboundChancesOffensive: int
    reboundChancesDefensive: int
    reboundChancesTotal: int
    touches: int
    secondaryAssists: int
    freeThrowAssists: int
    passes: int
    assists: int
    contestedFieldGoalsMade: int
    contestedFieldGoalsAttempted: int
    contestedFieldGoalPercentage: float
    uncontestedFieldGoalsMade: int
    uncontestedFieldGoalsAttempted: int
    uncontestedFieldGoalsPercentage: float
    fieldGoalPercentage: float
    defendedAtRimFieldGoalsMade: int
    defendedAtRimFieldGoalsAttempted: int
    defendedAtRimFieldGoalPercentage: float
