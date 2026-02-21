"""Models for the box score misc v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.box_score_v3 import (
    BoxScoreDataV3Base,
    BoxScorePlayerV3,
    BoxScoreTeamV3,
)
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class MiscStatisticsV3(BaseModel):
    """Miscellaneous box score statistics in V3 format."""

    minutes: str
    points_off_turnovers: int = Field(alias="pointsOffTurnovers")
    points_second_chance: int = Field(alias="pointsSecondChance")
    points_fast_break: int = Field(alias="pointsFastBreak")
    points_paint: int = Field(alias="pointsPaint")
    opp_points_off_turnovers: int = Field(alias="oppPointsOffTurnovers")
    opp_points_second_chance: int = Field(alias="oppPointsSecondChance")
    opp_points_fast_break: int = Field(alias="oppPointsFastBreak")
    opp_points_paint: int = Field(alias="oppPointsPaint")
    blocks: int
    blocks_against: int = Field(alias="blocksAgainst")
    fouls_personal: int = Field(alias="foulsPersonal")
    fouls_drawn: int = Field(alias="foulsDrawn")


class MiscPlayerV3(BoxScorePlayerV3[MiscStatisticsV3]):
    """Player with miscellaneous statistics in V3 format."""


class MiscTeamV3(BoxScoreTeamV3[MiscStatisticsV3]):
    """Team with miscellaneous statistics in V3 format."""

    players: list[MiscPlayerV3]  # type: ignore[assignment]


class BoxScoreMiscV3Data(BoxScoreDataV3Base):
    """Miscellaneous box score data in V3 format."""

    home_team: MiscTeamV3 = Field(alias="homeTeam")
    away_team: MiscTeamV3 = Field(alias="awayTeam")


class BoxScoreMiscV3Response(FrozenResponse):
    """Response from the box score misc v3 endpoint.

    Contains miscellaneous stats (points off turnovers, fastbreak points,
    paint points, blocks against, fouls drawn) in modern nested JSON format.
    """

    meta: Meta
    box_score_misc: BoxScoreMiscV3Data = Field(alias="boxScoreMisc")
