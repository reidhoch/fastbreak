"""Models for the box score scoring v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.box_score_v3 import (
    BoxScoreDataV3Base,
    BoxScorePlayerV3,
    BoxScoreTeamV3,
)
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class ScoringStatisticsV3(BaseModel):
    """Scoring breakdown statistics in V3 format."""

    minutes: str
    percentage_field_goals_attempted_2pt: float = Field(
        alias="percentageFieldGoalsAttempted2pt"
    )
    percentage_field_goals_attempted_3pt: float = Field(
        alias="percentageFieldGoalsAttempted3pt"
    )
    percentage_points_2pt: float = Field(alias="percentagePoints2pt")
    percentage_points_midrange_2pt: float = Field(alias="percentagePointsMidrange2pt")
    percentage_points_3pt: float = Field(alias="percentagePoints3pt")
    percentage_points_fast_break: float = Field(alias="percentagePointsFastBreak")
    percentage_points_free_throw: float = Field(alias="percentagePointsFreeThrow")
    percentage_points_off_turnovers: float = Field(alias="percentagePointsOffTurnovers")
    percentage_points_paint: float = Field(alias="percentagePointsPaint")
    percentage_assisted_2pt: float = Field(alias="percentageAssisted2pt")
    percentage_unassisted_2pt: float = Field(alias="percentageUnassisted2pt")
    percentage_assisted_3pt: float = Field(alias="percentageAssisted3pt")
    percentage_unassisted_3pt: float = Field(alias="percentageUnassisted3pt")
    percentage_assisted_fgm: float = Field(alias="percentageAssistedFGM")
    percentage_unassisted_fgm: float = Field(alias="percentageUnassistedFGM")


class ScoringPlayerV3(BoxScorePlayerV3[ScoringStatisticsV3]):
    """Player with scoring statistics in V3 format."""


class ScoringTeamV3(BoxScoreTeamV3[ScoringStatisticsV3]):
    """Team with scoring statistics in V3 format."""

    players: list[ScoringPlayerV3]  # type: ignore[assignment]


class BoxScoreScoringV3Data(BoxScoreDataV3Base):
    """Scoring box score data in V3 format."""

    home_team: ScoringTeamV3 = Field(alias="homeTeam")
    away_team: ScoringTeamV3 = Field(alias="awayTeam")


class BoxScoreScoringV3Response(FrozenResponse):
    """Response from the box score scoring v3 endpoint.

    Contains scoring breakdown (2pt vs 3pt, assisted vs unassisted,
    paint points, fastbreak points) in modern nested JSON format.
    """

    meta: Meta
    box_score_scoring: BoxScoreScoringV3Data = Field(alias="boxScoreScoring")
