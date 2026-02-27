"""Models for the box score matchups v3 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.box_score_v3 import (
    BoxScorePlayerV3Base,
    BoxScoreTeamV3Base,
)
from fastbreak.models.common.matchup_statistics import MatchupStatistics
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class MatchupOpponentV3(BaseModel):
    """An opponent in a player's matchup list."""

    person_id: int = Field(alias="personId")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    name_i: str = Field(alias="nameI")
    player_slug: str = Field(alias="playerSlug")
    jersey_num: str = Field(alias="jerseyNum")
    statistics: MatchupStatistics


class MatchupsPlayerV3(BoxScorePlayerV3Base):
    """A player with their matchup data in V3 format."""

    matchups: list[MatchupOpponentV3]


class MatchupsTeamV3(BoxScoreTeamV3Base):
    """A team with player matchup data in V3 format.

    Note: Some fields are optional because the NBA API returns null values
    for certain games where this data was not tracked or is not yet available.
    """

    players: list[MatchupsPlayerV3]


class BoxScoreMatchupsV3Data(BaseModel):
    """Box score matchups data for V3 format."""

    game_id: str = Field(alias="gameId")
    away_team_id: int = Field(alias="awayTeamId")
    home_team_id: int = Field(alias="homeTeamId")
    home_team: MatchupsTeamV3 = Field(alias="homeTeam")
    away_team: MatchupsTeamV3 = Field(alias="awayTeam")


class BoxScoreMatchupsV3Response(FrozenResponse):
    """Response from the boxscorematchupsv3 endpoint (preferred snake_case variant).

    Contains detailed player-vs-player matchup data in modern nested
    JSON format. Shows who guarded whom and with what results, including
    shooting percentages, assists, turnovers, and help defense stats.

    This is the preferred response model for the boxscorematchupsv3 API path,
    superseding the legacy BoxScoreMatchupsResponse which uses camelCase fields.
    """

    meta: Meta
    box_score_matchups: BoxScoreMatchupsV3Data = Field(alias="boxScoreMatchups")
