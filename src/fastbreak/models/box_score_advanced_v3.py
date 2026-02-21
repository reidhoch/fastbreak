"""Models for the box score advanced v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.box_score_v3 import (
    BoxScoreDataV3Base,
    BoxScorePlayerV3,
    BoxScoreTeamV3,
)
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class AdvancedStatisticsV3(BaseModel):
    """Advanced box score statistics in V3 format."""

    minutes: str
    estimated_offensive_rating: float = Field(alias="estimatedOffensiveRating")
    offensive_rating: float = Field(alias="offensiveRating")
    estimated_defensive_rating: float = Field(alias="estimatedDefensiveRating")
    defensive_rating: float = Field(alias="defensiveRating")
    estimated_net_rating: float = Field(alias="estimatedNetRating")
    net_rating: float = Field(alias="netRating")
    assist_percentage: float = Field(alias="assistPercentage")
    assist_to_turnover: float = Field(alias="assistToTurnover")
    assist_ratio: float = Field(alias="assistRatio")
    offensive_rebound_percentage: float = Field(alias="offensiveReboundPercentage")
    defensive_rebound_percentage: float = Field(alias="defensiveReboundPercentage")
    rebound_percentage: float = Field(alias="reboundPercentage")
    turnover_ratio: float = Field(alias="turnoverRatio")
    effective_field_goal_percentage: float = Field(alias="effectiveFieldGoalPercentage")
    true_shooting_percentage: float = Field(alias="trueShootingPercentage")
    usage_percentage: float = Field(alias="usagePercentage")
    estimated_usage_percentage: float = Field(alias="estimatedUsagePercentage")
    estimated_pace: float = Field(alias="estimatedPace")
    pace: float
    pace_per40: float = Field(alias="pacePer40")
    possessions: float
    pie: float = Field(alias="PIE")


class AdvancedPlayerV3(BoxScorePlayerV3[AdvancedStatisticsV3]):
    """Player with advanced statistics in V3 format."""


class AdvancedTeamV3(BoxScoreTeamV3[AdvancedStatisticsV3]):
    """Team with advanced statistics in V3 format."""

    players: list[AdvancedPlayerV3]  # type: ignore[assignment]


class BoxScoreAdvancedV3Data(BoxScoreDataV3Base):
    """Advanced box score data in V3 format."""

    home_team: AdvancedTeamV3 = Field(alias="homeTeam")
    away_team: AdvancedTeamV3 = Field(alias="awayTeam")


class BoxScoreAdvancedV3Response(FrozenResponse):
    """Response from the box score advanced v3 endpoint.

    Contains advanced analytics (offensive/defensive ratings, pace, PIE, etc.)
    in modern nested JSON format.
    """

    meta: Meta
    box_score_advanced: BoxScoreAdvancedV3Data = Field(alias="boxScoreAdvanced")
