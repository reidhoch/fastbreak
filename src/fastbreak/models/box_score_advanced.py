from pydantic import BaseModel

from fastbreak.models.advanced_statistics import (
    AdvancedStatistics,
    AdvancedTeamStatistics,
)
from fastbreak.models.meta import Meta


class AdvancedPlayer(BaseModel):
    """Player with advanced statistics."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    statistics: AdvancedStatistics


class AdvancedTeam(BaseModel):
    """Team with advanced statistics."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[AdvancedPlayer]
    statistics: AdvancedTeamStatistics


class BoxScoreAdvancedData(BaseModel):
    """Box score advanced data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: AdvancedTeam
    awayTeam: AdvancedTeam


class BoxScoreAdvancedResponse(BaseModel):
    """Response from the boxscoreadvancedv3 endpoint."""

    meta: Meta
    boxScoreAdvanced: BoxScoreAdvancedData
