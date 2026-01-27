from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin


class AdvancedStatistics(PandasMixin, PolarsMixin, BaseModel):
    """Advanced statistics for a player in a box score."""

    minutes: str
    estimatedOffensiveRating: float
    offensiveRating: float
    estimatedDefensiveRating: float
    defensiveRating: float
    estimatedNetRating: float
    netRating: float
    assistPercentage: float
    assistToTurnover: float
    assistRatio: float
    offensiveReboundPercentage: float
    defensiveReboundPercentage: float
    reboundPercentage: float
    turnoverRatio: float
    effectiveFieldGoalPercentage: float
    trueShootingPercentage: float
    usagePercentage: float
    estimatedUsagePercentage: float
    estimatedPace: float
    pace: float
    pacePer40: float
    possessions: float
    PIE: float


class AdvancedTeamStatistics(AdvancedStatistics):
    """Advanced statistics for a team in a box score."""

    estimatedTeamTurnoverPercentage: float
