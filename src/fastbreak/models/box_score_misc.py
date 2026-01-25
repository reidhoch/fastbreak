from pydantic import BaseModel

from fastbreak.models.common.meta import Meta
from fastbreak.models.common.misc_statistics import MiscStatistics


class MiscPlayer(BaseModel):
    """Player with miscellaneous statistics."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    statistics: MiscStatistics


class MiscTeam(BaseModel):
    """Team with players and miscellaneous statistics."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[MiscPlayer]
    statistics: MiscStatistics


class BoxScoreMiscData(BaseModel):
    """Box score miscellaneous data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: MiscTeam
    awayTeam: MiscTeam


class BoxScoreMiscResponse(BaseModel):
    """Response from the boxscoremisc endpoint."""

    meta: Meta
    boxScoreMisc: BoxScoreMiscData
