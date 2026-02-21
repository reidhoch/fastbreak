"""Models for the box score traditional v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.box_score_v3 import (
    BoxScoreDataV3Base,
    BoxScorePlayerV3,
    BoxScoreTeamV3,
)
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class TraditionalStatisticsV3(BaseModel):
    """Traditional box score statistics in V3 format."""

    minutes: str
    field_goals_made: int = Field(alias="fieldGoalsMade")
    field_goals_attempted: int = Field(alias="fieldGoalsAttempted")
    field_goals_percentage: float = Field(alias="fieldGoalsPercentage")
    three_pointers_made: int = Field(alias="threePointersMade")
    three_pointers_attempted: int = Field(alias="threePointersAttempted")
    three_pointers_percentage: float = Field(alias="threePointersPercentage")
    free_throws_made: int = Field(alias="freeThrowsMade")
    free_throws_attempted: int = Field(alias="freeThrowsAttempted")
    free_throws_percentage: float = Field(alias="freeThrowsPercentage")
    rebounds_offensive: int = Field(alias="reboundsOffensive")
    rebounds_defensive: int = Field(alias="reboundsDefensive")
    rebounds_total: int = Field(alias="reboundsTotal")
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fouls_personal: int = Field(alias="foulsPersonal")
    points: int
    plus_minus_points: float = Field(alias="plusMinusPoints")


class TraditionalPlayerV3(BoxScorePlayerV3[TraditionalStatisticsV3]):
    """Player with traditional statistics in V3 format."""


class TraditionalTeamV3(BoxScoreTeamV3[TraditionalStatisticsV3]):
    """Team with traditional statistics in V3 format."""

    players: list[TraditionalPlayerV3]  # type: ignore[assignment]


class BoxScoreTraditionalV3Data(BoxScoreDataV3Base):
    """Traditional box score data in V3 format."""

    home_team: TraditionalTeamV3 = Field(alias="homeTeam")
    away_team: TraditionalTeamV3 = Field(alias="awayTeam")


class BoxScoreTraditionalV3Response(FrozenResponse):
    """Response from the box score traditional v3 endpoint.

    Contains traditional box score stats (points, rebounds, assists, etc.)
    in modern nested JSON format.
    """

    meta: Meta
    box_score_traditional: BoxScoreTraditionalV3Data = Field(
        alias="boxScoreTraditional"
    )
