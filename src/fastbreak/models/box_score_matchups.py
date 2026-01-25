from pydantic import BaseModel

from fastbreak.models.common.matchup_statistics import MatchupStatistics
from fastbreak.models.common.meta import Meta


class MatchupOpponent(BaseModel):
    """Opponent player in a matchup with their statistics."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    jerseyNum: str
    statistics: MatchupStatistics


class MatchupsPlayer(BaseModel):
    """Player with their defensive matchups."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    matchups: list[MatchupOpponent]


class MatchupsTeam(BaseModel):
    """Team with players and their matchups."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[MatchupsPlayer]


class BoxScoreMatchupsData(BaseModel):
    """Box score matchups data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: MatchupsTeam
    awayTeam: MatchupsTeam


class BoxScoreMatchupsResponse(BaseModel):
    """Response from the boxscorematchupsv3 endpoint."""

    meta: Meta
    boxScoreMatchups: BoxScoreMatchupsData
