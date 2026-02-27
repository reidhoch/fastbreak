"""Models for the box score hustle v2 endpoint."""

from pydantic import BaseModel, Field

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class HustleStatistics(BaseModel):
    """Hustle statistics for a player or team."""

    minutes: str
    points: int
    contested_shots: int = Field(alias="contestedShots")
    contested_shots_2pt: int = Field(alias="contestedShots2pt")
    contested_shots_3pt: int = Field(alias="contestedShots3pt")
    deflections: int
    charges_drawn: int = Field(alias="chargesDrawn")
    screen_assists: int = Field(alias="screenAssists")
    screen_assist_points: int = Field(alias="screenAssistPoints")
    loose_balls_recovered_offensive: int = Field(alias="looseBallsRecoveredOffensive")
    loose_balls_recovered_defensive: int = Field(alias="looseBallsRecoveredDefensive")
    loose_balls_recovered_total: int = Field(alias="looseBallsRecoveredTotal")
    offensive_box_outs: int = Field(alias="offensiveBoxOuts")
    defensive_box_outs: int = Field(alias="defensiveBoxOuts")
    box_out_player_team_rebounds: int = Field(alias="boxOutPlayerTeamRebounds")
    box_out_player_rebounds: int = Field(alias="boxOutPlayerRebounds")
    box_outs: int = Field(alias="boxOuts")


class HustlePlayer(PandasMixin, PolarsMixin, BaseModel):
    """Player with hustle statistics from a box score."""

    person_id: int = Field(alias="personId")
    first_name: str = Field(alias="firstName")
    family_name: str = Field(alias="familyName")
    name_i: str = Field(alias="nameI")
    player_slug: str = Field(alias="playerSlug")
    position: str
    comment: str
    jersey_num: str = Field(alias="jerseyNum")
    statistics: HustleStatistics


class HustleTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with hustle statistics from a box score.

    Note: Some fields are optional because the NBA API returns null values
    for certain games where this data was not tracked or is not yet available.
    """

    team_id: int = Field(alias="teamId")
    team_city: str | None = Field(None, alias="teamCity")
    team_name: str | None = Field(None, alias="teamName")
    team_tricode: str | None = Field(None, alias="teamTricode")
    team_slug: str | None = Field(None, alias="teamSlug")
    players: list[HustlePlayer]
    statistics: HustleStatistics


class BoxScoreHustleData(BaseModel):
    """Box score hustle data containing both teams."""

    game_id: str = Field(alias="gameId")
    away_team_id: int = Field(alias="awayTeamId")
    home_team_id: int = Field(alias="homeTeamId")
    home_team: HustleTeam = Field(alias="homeTeam")
    away_team: HustleTeam = Field(alias="awayTeam")


class BoxScoreHustleResponse(FrozenResponse):
    """Response from the box score hustle v2 endpoint.

    Contains hustle statistics for all players and both teams in a game,
    organized by home and away team with nested player data.

    The v2 format uses modern nested JSON rather than the traditional
    result sets format, providing additional player metadata like
    first/last names and player slugs.
    """

    meta: Meta
    box_score_hustle: BoxScoreHustleData = Field(alias="boxScoreHustle")
