from pydantic import BaseModel

from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.four_factors_statistics import FourFactorsStatistics
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class FourFactorsPlayer(PandasMixin, PolarsMixin, BaseModel):
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


class FourFactorsTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with four factors statistics.

    Note: Some fields are optional because the NBA API returns null values
    for certain games where this data was not tracked or is not yet available.
    """

    teamId: int
    teamCity: str | None = None
    teamName: str | None = None
    teamTricode: str | None = None
    teamSlug: str | None = None
    players: list[FourFactorsPlayer]
    statistics: FourFactorsStatistics


class BoxScoreFourFactorsData(PandasMixin, PolarsMixin, BaseModel):
    """Box score four factors data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: FourFactorsTeam
    awayTeam: FourFactorsTeam


class BoxScoreFourFactorsResponse(FrozenResponse):
    """Response from the boxscorefourfactorsv3 endpoint."""

    meta: Meta
    boxScoreFourFactors: BoxScoreFourFactorsData
