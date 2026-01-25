from pydantic import BaseModel


class FourFactorsStatistics(BaseModel):
    """Four factors statistics for a player or team.

    The four factors are: effective FG%, free throw rate,
    turnover percentage, and offensive rebound percentage.
    Also includes opponent (defensive) versions of each.
    """

    minutes: str
    effectiveFieldGoalPercentage: float
    freeThrowAttemptRate: float
    teamTurnoverPercentage: float
    offensiveReboundPercentage: float
    oppEffectiveFieldGoalPercentage: float
    oppFreeThrowAttemptRate: float
    oppTeamTurnoverPercentage: float
    oppOffensiveReboundPercentage: float
