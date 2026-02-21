"""Models for the box score player track v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.box_score_v3 import (
    BoxScoreDataV3Base,
    BoxScorePlayerV3,
    BoxScoreTeamV3Base,
)
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class PlayerTrackStatisticsV3(BaseModel):
    """Player tracking statistics in V3 format."""

    minutes: str
    speed: float
    distance: float
    rebound_chances_offensive: int = Field(alias="reboundChancesOffensive")
    rebound_chances_defensive: int = Field(alias="reboundChancesDefensive")
    rebound_chances_total: int = Field(alias="reboundChancesTotal")
    touches: int
    secondary_assists: int = Field(alias="secondaryAssists")
    free_throw_assists: int = Field(alias="freeThrowAssists")
    passes: int
    assists: int
    contested_field_goals_made: int = Field(alias="contestedFieldGoalsMade")
    contested_field_goals_attempted: int = Field(alias="contestedFieldGoalsAttempted")
    contested_field_goal_percentage: float = Field(alias="contestedFieldGoalPercentage")
    uncontested_field_goals_made: int = Field(alias="uncontestedFieldGoalsMade")
    uncontested_field_goals_attempted: int = Field(
        alias="uncontestedFieldGoalsAttempted"
    )
    uncontested_field_goals_percentage: float = Field(
        alias="uncontestedFieldGoalsPercentage"
    )
    field_goal_percentage: float = Field(alias="fieldGoalPercentage")
    defended_at_rim_field_goals_made: int = Field(alias="defendedAtRimFieldGoalsMade")
    defended_at_rim_field_goals_attempted: int = Field(
        alias="defendedAtRimFieldGoalsAttempted"
    )
    defended_at_rim_field_goal_percentage: float = Field(
        alias="defendedAtRimFieldGoalPercentage"
    )


class PlayerTrackTeamStatisticsV3(BaseModel):
    """Team-level tracking statistics in V3 format (no speed)."""

    minutes: str
    distance: float
    rebound_chances_offensive: int = Field(alias="reboundChancesOffensive")
    rebound_chances_defensive: int = Field(alias="reboundChancesDefensive")
    rebound_chances_total: int = Field(alias="reboundChancesTotal")
    touches: int
    secondary_assists: int = Field(alias="secondaryAssists")
    free_throw_assists: int = Field(alias="freeThrowAssists")
    passes: int
    assists: int
    contested_field_goals_made: int = Field(alias="contestedFieldGoalsMade")
    contested_field_goals_attempted: int = Field(alias="contestedFieldGoalsAttempted")
    contested_field_goal_percentage: float = Field(alias="contestedFieldGoalPercentage")
    uncontested_field_goals_made: int = Field(alias="uncontestedFieldGoalsMade")
    uncontested_field_goals_attempted: int = Field(
        alias="uncontestedFieldGoalsAttempted"
    )
    uncontested_field_goals_percentage: float = Field(
        alias="uncontestedFieldGoalsPercentage"
    )
    field_goal_percentage: float = Field(alias="fieldGoalPercentage")
    defended_at_rim_field_goals_made: int = Field(alias="defendedAtRimFieldGoalsMade")
    defended_at_rim_field_goals_attempted: int = Field(
        alias="defendedAtRimFieldGoalsAttempted"
    )
    defended_at_rim_field_goal_percentage: float = Field(
        alias="defendedAtRimFieldGoalPercentage"
    )


class PlayerTrackPlayerV3(BoxScorePlayerV3[PlayerTrackStatisticsV3]):
    """Player with tracking statistics in V3 format."""


class PlayerTrackTeamV3(BoxScoreTeamV3Base, PandasMixin, PolarsMixin):
    """Team with tracking statistics in V3 format."""

    players: list[PlayerTrackPlayerV3]
    statistics: PlayerTrackTeamStatisticsV3


class BoxScorePlayerTrackV3Data(BoxScoreDataV3Base):
    """Player tracking box score data in V3 format."""

    home_team: PlayerTrackTeamV3 = Field(alias="homeTeam")
    away_team: PlayerTrackTeamV3 = Field(alias="awayTeam")


class BoxScorePlayerTrackV3Response(FrozenResponse):
    """Response from the box score player track v3 endpoint.

    Contains player tracking data (speed, distance, touches, contested shots,
    rim protection) in modern nested JSON format.
    """

    meta: Meta
    box_score_player_track: BoxScorePlayerTrackV3Data = Field(
        alias="boxScorePlayerTrack"
    )
