from pydantic import BaseModel

from fastbreak.models.common.four_factors_statistics import FourFactorsStatistics
from fastbreak.models.common.meta import Meta


class FourFactorsPlayer(BaseModel):
    """Player with four factors statistics."""

    personId: int
    firstName: str
    familyName: str
    nameI: str
    playerSlug: str
    position: str
    comment: str
    jerseyNum: str
    statistics: FourFactorsStatistics


class FourFactorsTeam(BaseModel):
    """Team with four factors statistics."""

    teamId: int
    teamCity: str
    teamName: str
    teamTricode: str
    teamSlug: str
    players: list[FourFactorsPlayer]
    statistics: FourFactorsStatistics


class BoxScoreFourFactorsData(BaseModel):
    """Box score four factors data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: FourFactorsTeam
    awayTeam: FourFactorsTeam


class BoxScoreFourFactorsResponse(BaseModel):
    """Response from the boxscorefourfactorsv3 endpoint."""

    meta: Meta
    boxScoreFourFactors: BoxScoreFourFactorsData
