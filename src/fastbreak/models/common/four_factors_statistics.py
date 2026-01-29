from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class FourFactorsStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Four factors statistics for a player or team.

    The four factors are: effective FG%, free throw rate,
    turnover percentage, and offensive rebound percentage.
    Also includes opponent (defensive) versions of each.
    """

    minutes: str
    effectiveFieldGoalPercentage: float = Field(ge=0.0, le=1.0)
    freeThrowAttemptRate: float = Field(ge=0.0)
    teamTurnoverPercentage: float = Field(ge=0.0, le=1.0)
    offensiveReboundPercentage: float = Field(ge=0.0, le=1.0)
    oppEffectiveFieldGoalPercentage: float = Field(ge=0.0, le=1.0)
    oppFreeThrowAttemptRate: float = Field(ge=0.0)
    oppTeamTurnoverPercentage: float = Field(ge=0.0, le=1.0)
    oppOffensiveReboundPercentage: float = Field(ge=0.0, le=1.0)
