from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class FourFactorsStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Four factors statistics for a player or team.

    The four factors are: effective FG%, free throw rate,
    turnover percentage, and offensive rebound percentage.
    Also includes opponent (defensive) versions of each.
    """

    minutes: str
    # eFG% can exceed 1.0 on small samples with many 3-pointers; no upper bound.
    effectiveFieldGoalPercentage: float = Field(ge=0.0)
    freeThrowAttemptRate: float = Field(ge=0.0)
    # Box score four-factors endpoint returns TOV% as a 0-1 fraction (e.g.
    # 0.126 for 12.6%), unlike AdvancedTeamStatistics.estimatedTeamTurnoverPercentage
    # which the advanced endpoint returns on a 0-100 scale.
    teamTurnoverPercentage: float = Field(ge=0.0, le=1.0)
    offensiveReboundPercentage: float = Field(ge=0.0, le=1.0)
    oppEffectiveFieldGoalPercentage: float = Field(ge=0.0, le=1.0)
    oppFreeThrowAttemptRate: float = Field(ge=0.0)
    oppTeamTurnoverPercentage: float = Field(ge=0.0, le=1.0)
    oppOffensiveReboundPercentage: float = Field(ge=0.0, le=1.0)
