from pydantic import BaseModel, Field

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
    assistPercentage: float = Field(ge=0.0)  # Relaxed - edge cases exist
    assistToTurnover: float = Field(ge=0.0)
    assistRatio: float = Field(ge=0.0)
    offensiveReboundPercentage: float = Field(ge=0.0)  # Relaxed - edge cases exist
    defensiveReboundPercentage: float = Field(ge=0.0)  # Relaxed - edge cases exist
    reboundPercentage: float = Field(ge=0.0)  # Relaxed - edge cases exist
    turnoverRatio: float = Field(ge=0.0)
    # eFG% can exceed 1.0 with 3-pointers
    effectiveFieldGoalPercentage: float = Field(ge=0.0)
    # ts% can exceed 1.0 with efficient FT shooting
    trueShootingPercentage: float = Field(ge=0.0)
    usagePercentage: float = Field(ge=0.0)  # Estimates can exceed 1.0
    estimatedUsagePercentage: float = Field(ge=0.0)  # Estimates can exceed 1.0
    estimatedPace: float = Field(ge=0.0)
    pace: float = Field(ge=0.0)
    pacePer40: float = Field(ge=0.0)
    possessions: float = Field(ge=0.0)
    PIE: float  # Player Impact Estimate, can be negative


class AdvancedTeamStatistics(AdvancedStatistics):
    """Advanced statistics for a team in a box score."""

    # NBA advanced box-score endpoint returns this on a 0-100 scale (e.g. 12.6
    # for 12.6%), unlike FourFactorsStatistics.teamTurnoverPercentage which uses
    # a 0-1 fraction. metrics.tov_pct() also returns 0-1; multiply by 100 before
    # comparing against this field.
    estimatedTeamTurnoverPercentage: float = Field(ge=0.0, le=100.0)
