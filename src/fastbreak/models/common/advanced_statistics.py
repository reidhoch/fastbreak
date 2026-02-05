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
    effectiveFieldGoalPercentage: float = Field(
        ge=0.0
    )  # Can exceed 1.0 with 3-pointers
    trueShootingPercentage: float = Field(
        ge=0.0
    )  # Can exceed 1.0 with efficient FT shooting
    usagePercentage: float = Field(ge=0.0)  # Estimates can exceed 1.0
    estimatedUsagePercentage: float = Field(ge=0.0)  # Estimates can exceed 1.0
    estimatedPace: float = Field(ge=0.0)
    pace: float = Field(ge=0.0)
    pacePer40: float = Field(ge=0.0)
    possessions: float = Field(ge=0.0)
    PIE: float  # Player Impact Estimate, can be negative


class AdvancedTeamStatistics(AdvancedStatistics):
    """Advanced statistics for a team in a box score."""

    estimatedTeamTurnoverPercentage: float = Field(ge=0.0, le=100.0)
