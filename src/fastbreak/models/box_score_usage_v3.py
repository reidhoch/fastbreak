"""Models for the box score usage v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.box_score_v3 import (
    BoxScoreDataV3Base,
    BoxScorePlayerV3,
    BoxScoreTeamV3,
)
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class UsageStatisticsV3(BaseModel):
    """Usage/share statistics in V3 format."""

    minutes: str
    usage_percentage: float = Field(alias="usagePercentage")
    percentage_field_goals_made: float = Field(alias="percentageFieldGoalsMade")
    percentage_field_goals_attempted: float = Field(
        alias="percentageFieldGoalsAttempted"
    )
    percentage_three_pointers_made: float = Field(alias="percentageThreePointersMade")
    percentage_three_pointers_attempted: float = Field(
        alias="percentageThreePointersAttempted"
    )
    percentage_free_throws_made: float = Field(alias="percentageFreeThrowsMade")
    percentage_free_throws_attempted: float = Field(
        alias="percentageFreeThrowsAttempted"
    )
    percentage_rebounds_offensive: float = Field(alias="percentageReboundsOffensive")
    percentage_rebounds_defensive: float = Field(alias="percentageReboundsDefensive")
    percentage_rebounds_total: float = Field(alias="percentageReboundsTotal")
    percentage_assists: float = Field(alias="percentageAssists")
    percentage_turnovers: float = Field(alias="percentageTurnovers")
    percentage_steals: float = Field(alias="percentageSteals")
    percentage_blocks: float = Field(alias="percentageBlocks")
    percentage_blocks_allowed: float = Field(alias="percentageBlocksAllowed")
    percentage_personal_fouls: float = Field(alias="percentagePersonalFouls")
    percentage_personal_fouls_drawn: float = Field(alias="percentagePersonalFoulsDrawn")
    percentage_points: float = Field(alias="percentagePoints")


class UsagePlayerV3(BoxScorePlayerV3[UsageStatisticsV3]):
    """Player with usage statistics in V3 format."""


class UsageTeamV3(BoxScoreTeamV3[UsageStatisticsV3]):
    """Team with usage statistics in V3 format."""

    players: list[UsagePlayerV3]  # type: ignore[assignment]


class BoxScoreUsageV3Data(BoxScoreDataV3Base):
    """Usage box score data in V3 format."""

    home_team: UsageTeamV3 = Field(alias="homeTeam")
    away_team: UsageTeamV3 = Field(alias="awayTeam")


class BoxScoreUsageV3Response(FrozenResponse):
    """Response from the box score usage v3 endpoint.

    Contains player share/usage rates (% of team stats while on court)
    in modern nested JSON format.
    """

    meta: Meta
    box_score_usage: BoxScoreUsageV3Data = Field(alias="boxScoreUsage")
