from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class MatchupStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Statistics for a specific player-vs-player defensive matchup."""

    matchupMinutes: str
    matchupMinutesSort: float
    partialPossessions: float
    percentageDefenderTotalTime: float
    percentageOffensiveTotalTime: float
    percentageTotalTimeBothOn: float
    switchesOn: int
    playerPoints: int
    teamPoints: int
    matchupAssists: int
    matchupPotentialAssists: int
    matchupTurnovers: int
    matchupBlocks: int
    matchupFieldGoalsMade: int
    matchupFieldGoalsAttempted: int
    matchupFieldGoalsPercentage: float
    matchupThreePointersMade: int
    matchupThreePointersAttempted: int
    matchupThreePointersPercentage: float
    helpBlocks: int
    helpFieldGoalsMade: int
    helpFieldGoalsAttempted: int
    helpFieldGoalsPercentage: float
    matchupFreeThrowsMade: int
    matchupFreeThrowsAttempted: int
    shootingFouls: int
