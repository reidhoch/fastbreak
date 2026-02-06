from pydantic import BaseModel

from fastbreak.models.common.advanced_statistics import (
    AdvancedStatistics,
    AdvancedTeamStatistics,
)
from fastbreak.models.common.dataframe import PandasMixin, PolarsMixin
from fastbreak.models.common.meta import Meta
from fastbreak.models.common.response import FrozenResponse


class AdvancedPlayer(PandasMixin, PolarsMixin, BaseModel):
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


class AdvancedTeam(PandasMixin, PolarsMixin, BaseModel):
    """Team with advanced statistics.

    Note: Some fields are optional because the NBA API returns null values
    for certain old games (e.g., games from 2003-04 and 2012-13 seasons)
    where this data was not tracked or digitized.
    """

    teamId: int
    teamCity: str | None = None
    teamName: str | None = None
    teamTricode: str | None = None
    teamSlug: str | None = None
    players: list[AdvancedPlayer]
    statistics: AdvancedTeamStatistics | None = None


class BoxScoreAdvancedData(PandasMixin, PolarsMixin, BaseModel):
    """Box score advanced data for a game."""

    gameId: str
    awayTeamId: int
    homeTeamId: int
    homeTeam: AdvancedTeam
    awayTeam: AdvancedTeam


class BoxScoreAdvancedResponse(FrozenResponse):
    """Response from the boxscoreadvancedv3 endpoint."""

    meta: Meta
    boxScoreAdvanced: BoxScoreAdvancedData
